# Auto-Refresh Implementation Plan

## Goal
Enable automatic blueprint re-export when blueprints are modified in UE5, requiring only a single command to start monitoring.

## User Experience Target

**Current (Manual):**
```
1. Make blueprint changes
2. Run export command
3. Repeat steps 1-2 for every change
```

**Target (Auto-Refresh):**
```
1. Run command ONCE: start_auto_export()
2. Make blueprint changes → Auto-exports in background
3. Keep working, files stay synced
4. (Optional) Run stop_auto_export() when done
```

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│   UE5 Asset Registry                │
│   - Monitors all asset changes      │
└──────────────┬──────────────────────┘
               │ fires callbacks
               ▼
┌─────────────────────────────────────┐
│   Auto-Refresh Monitor              │
│   - OnAssetUpdated callback         │
│   - Debounce timer (2s)             │
│   - Blueprint filter                │
└──────────────┬──────────────────────┘
               │ triggers export
               ▼
┌─────────────────────────────────────┐
│   Blueprint Exporter                │
│   - Exports changed blueprint       │
│   - Generates JSON + Markdown       │
└─────────────────────────────────────┘
```

---

## Implementation Approaches

### Approach 1: Slate Tick Callback (Recommended)
**Pros:**
- Runs on editor tick, doesn't block
- Easy to start/stop
- Native UE5 pattern

**Cons:**
- Slight performance overhead (minimal)

### Approach 2: Asset Registry Callbacks
**Pros:**
- Event-driven, no polling
- Very efficient

**Cons:**
- More complex to manage state

### Approach 3: Editor Utility Widget Timer
**Pros:**
- Visual UI to start/stop
- User-friendly

**Cons:**
- Requires widget creation
- More setup for users

**Decision: Use Approach 1 + Approach 2 Hybrid**

---

## Detailed Implementation

### Phase 1: Core Auto-Refresh System

#### 1.1 Global State Management

```python
# Global state for the auto-refresh monitor
_auto_refresh_state = {
    'active': False,
    'tick_handle': None,
    'last_export_time': {},  # blueprint_path -> timestamp
    'pending_exports': set(),  # blueprints to export
    'debounce_seconds': 2.0,
    'export_count': 0
}
```

#### 1.2 Asset Registry Callbacks

```python
def on_asset_updated(asset_data):
    """Called when any asset is updated"""
    # Filter for blueprints only
    if not is_blueprint_asset(asset_data):
        return

    blueprint_path = asset_data.package_name

    # Add to pending exports
    _auto_refresh_state['pending_exports'].add(blueprint_path)

    unreal.log(f"Blueprint modified: {blueprint_path}")
```

#### 1.3 Tick-Based Export Processing

```python
def auto_refresh_tick(delta_time):
    """Called every frame while auto-refresh is active"""

    if not _auto_refresh_state['pending_exports']:
        return

    current_time = time.time()
    debounce = _auto_refresh_state['debounce_seconds']

    # Process pending exports (with debouncing)
    blueprints_to_export = []

    for bp_path in list(_auto_refresh_state['pending_exports']):
        last_export = _auto_refresh_state['last_export_time'].get(bp_path, 0)

        # Has enough time passed since last export?
        if current_time - last_export >= debounce:
            blueprints_to_export.append(bp_path)
            _auto_refresh_state['pending_exports'].remove(bp_path)
            _auto_refresh_state['last_export_time'][bp_path] = current_time

    # Export the blueprints
    for bp_path in blueprints_to_export:
        export_single_blueprint_by_path(bp_path)
        _auto_refresh_state['export_count'] += 1
```

#### 1.4 Start/Stop Functions

```python
def start_auto_export():
    """Start monitoring blueprints for changes"""

    if _auto_refresh_state['active']:
        unreal.log_warning("Auto-export already running!")
        return

    # Register asset registry callbacks
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_registry.on_asset_updated().add_callable(on_asset_updated)

    # Register tick callback
    tick_handle = unreal.register_slate_post_tick_callback(auto_refresh_tick)

    _auto_refresh_state['active'] = True
    _auto_refresh_state['tick_handle'] = tick_handle
    _auto_refresh_state['export_count'] = 0

    unreal.log("=" * 60)
    unreal.log("AUTO-EXPORT STARTED!")
    unreal.log("=" * 60)
    unreal.log("Blueprints will automatically export when you save changes.")
    unreal.log("To stop: run stop_auto_export()")
    unreal.log("=" * 60)


def stop_auto_export():
    """Stop monitoring blueprints"""

    if not _auto_refresh_state['active']:
        unreal.log_warning("Auto-export not running!")
        return

    # Unregister callbacks
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_registry.on_asset_updated().remove_callable(on_asset_updated)

    if _auto_refresh_state['tick_handle']:
        unreal.unregister_slate_post_tick_callback(_auto_refresh_state['tick_handle'])

    _auto_refresh_state['active'] = False
    _auto_refresh_state['tick_handle'] = None

    unreal.log("=" * 60)
    unreal.log("AUTO-EXPORT STOPPED")
    unreal.log(f"Total exports during session: {_auto_refresh_state['export_count']}")
    unreal.log("=" * 60)
```

---

### Phase 2: Enhanced Features

#### 2.1 Smart Debouncing

```python
# Configuration
DEBOUNCE_CONFIG = {
    'quick_edits': 2.0,      # Wait 2s after last change
    'batch_threshold': 5,    # If 5+ blueprints changed
    'batch_delay': 5.0       # Wait 5s for batch
}

def should_export_now(bp_path):
    """Determine if blueprint should export now or wait"""

    pending_count = len(_auto_refresh_state['pending_exports'])

    # Batch export if many changes
    if pending_count >= DEBOUNCE_CONFIG['batch_threshold']:
        return use_batch_delay()
    else:
        return use_quick_debounce()
```

#### 2.2 Export Queue with Priority

```python
class ExportPriority:
    HIGH = 0    # User is actively editing
    NORMAL = 1  # Regular saves
    LOW = 2     # Batch processing

def prioritize_exports():
    """Export most recently modified blueprints first"""

    pending = _auto_refresh_state['pending_exports']

    # Sort by last modified time (most recent first)
    sorted_blueprints = sorted(
        pending,
        key=lambda bp: get_last_modified_time(bp),
        reverse=True
    )

    return sorted_blueprints[:3]  # Export top 3 most recent
```

#### 2.3 Progress Notifications

```python
def show_export_notification(blueprint_name):
    """Show non-intrusive notification"""

    # Use UE5's notification system
    unreal.log(f"✓ Exported: {blueprint_name}")

    # Optional: Slate notification (non-blocking)
    # unreal.EditorDialog.show_message(
    #     "Blueprint Exported",
    #     f"{blueprint_name} synced to Claude Code",
    #     unreal.AppMsgType.OK
    # )
```

#### 2.4 Export Statistics

```python
def get_auto_export_stats():
    """Return statistics about auto-export session"""

    return {
        'active': _auto_refresh_state['active'],
        'total_exports': _auto_refresh_state['export_count'],
        'pending_exports': len(_auto_refresh_state['pending_exports']),
        'debounce_seconds': _auto_refresh_state['debounce_seconds']
    }


def print_stats():
    """Print current statistics"""
    stats = get_auto_export_stats()

    unreal.log("\n--- Auto-Export Stats ---")
    unreal.log(f"Status: {'RUNNING' if stats['active'] else 'STOPPED'}")
    unreal.log(f"Exports this session: {stats['total_exports']}")
    unreal.log(f"Pending: {stats['pending_exports']}")
    unreal.log(f"Debounce: {stats['debounce_seconds']}s")
```

---

### Phase 3: Configuration & Settings

#### 3.1 User Configuration File

```python
# config.json in Content/Python/
{
    "auto_export": {
        "enabled_by_default": false,
        "debounce_seconds": 2.0,
        "batch_threshold": 5,
        "batch_delay": 5.0,
        "show_notifications": true,
        "export_on_save_only": true,  # vs on every change
        "ignore_patterns": [
            "*_TEMP",
            "*_WIP"
        ]
    }
}
```

#### 3.2 Runtime Configuration

```python
def configure_auto_export(
    debounce_seconds=2.0,
    show_notifications=True,
    export_on_save_only=True
):
    """Configure auto-export behavior at runtime"""

    _auto_refresh_state['debounce_seconds'] = debounce_seconds
    _auto_refresh_state['show_notifications'] = show_notifications
    _auto_refresh_state['export_on_save_only'] = export_on_save_only

    unreal.log(f"Auto-export configured: debounce={debounce_seconds}s")
```

---

## Implementation Steps

### Step 1: Core Implementation (Week 1)
- [ ] Add global state dictionary
- [ ] Implement `on_asset_updated` callback
- [ ] Implement `auto_refresh_tick` function
- [ ] Implement `start_auto_export()` and `stop_auto_export()`
- [ ] Test with single blueprint changes

### Step 2: Debouncing & Filtering (Week 1)
- [ ] Add debounce timer logic
- [ ] Filter for blueprint assets only
- [ ] Add pending export queue
- [ ] Test with rapid changes

### Step 3: Enhanced Features (Week 2)
- [ ] Smart debouncing (batch detection)
- [ ] Export prioritization
- [ ] Progress notifications
- [ ] Statistics tracking

### Step 4: Configuration (Week 2)
- [ ] Add configuration file support
- [ ] Runtime configuration functions
- [ ] Ignore patterns
- [ ] User preferences

### Step 5: Testing & Polish (Week 3)
- [ ] Test with large projects (100+ blueprints)
- [ ] Test rapid editing scenarios
- [ ] Test batch saves
- [ ] Performance profiling
- [ ] Error handling

---

## User Commands

### Simple Usage

```python
# ONE-TIME SETUP - Run this once when you open your project
import sys; sys.path.append("/path/to/Content/Python")
import blueprint_watcher
blueprint_watcher.start_auto_export()

# Now just work normally - exports happen automatically!

# When done for the day (optional):
blueprint_watcher.stop_auto_export()
```

### Advanced Usage

```python
# Custom configuration
blueprint_watcher.configure_auto_export(
    debounce_seconds=3.0,      # Wait 3 seconds
    show_notifications=False   # Silent mode
)

blueprint_watcher.start_auto_export()

# Check stats
blueprint_watcher.print_stats()

# Pause and resume
blueprint_watcher.stop_auto_export()
blueprint_watcher.start_auto_export()
```

---

## Edge Cases & Error Handling

### 1. Editor Restart
**Problem:** Auto-export stops when editor restarts
**Solution:** Add to startup scripts in Project Settings

### 2. Blueprint Deletion
**Problem:** Deleted blueprints trigger callbacks
**Solution:** Check if blueprint still exists before export

### 3. Compilation Errors
**Problem:** Broken blueprints cause export errors
**Solution:** Try-catch in export, log error, skip

### 4. Performance with Large Projects
**Problem:** 500+ blueprints can slow things down
**Solution:** Only export changed blueprints, not full export

### 5. Conflicting Changes
**Problem:** Blueprint changed while exporting
**Solution:** Use file locking, retry on next tick

---

## Performance Considerations

### Memory Usage
- State dictionary: ~1KB per 100 blueprints
- Tick callback: Minimal overhead (runs once per frame)
- Asset callbacks: Event-driven, no overhead when idle

### CPU Usage
- Tick check: <0.1ms per frame when no exports pending
- Export operation: 10-50ms per blueprint (existing cost)
- Batch export: 100-500ms for 10 blueprints

### Optimization Strategies
1. Only export changed blueprints (not full project)
2. Debounce to batch multiple changes
3. Export in background (don't block editor)
4. Cache recent exports to avoid duplicates

---

## Testing Plan

### Unit Tests
```python
def test_debounce():
    # Rapid changes should batch
    assert pending_exports_after_rapid_changes() == 1

def test_blueprint_filtering():
    # Only blueprints trigger export
    assert non_blueprint_changes_ignored()

def test_start_stop():
    # Can start and stop cleanly
    assert can_restart_multiple_times()
```

### Integration Tests
- Test with real UE5 project
- Make 10 blueprint changes rapidly
- Verify only exports after debounce period
- Check file timestamps
- Verify no duplicates

### Performance Tests
- Monitor CPU usage during active editing
- Test with 100+ blueprint project
- Verify <5% CPU overhead
- Check memory doesn't leak over time

---

## Rollout Strategy

### Phase 1: MVP (This Week)
- Basic auto-refresh with fixed 2s debounce
- Start/stop commands
- Simple notifications

### Phase 2: Enhanced (Next Week)
- Smart debouncing
- Configuration options
- Statistics

### Phase 3: Production (Week 3)
- Full error handling
- Startup script integration
- Documentation
- Video tutorial

---

## Success Metrics

**Primary:**
- ✅ User runs command once, exports work automatically
- ✅ Changes appear in Claude Code within 3 seconds
- ✅ No performance impact on editor

**Secondary:**
- ✅ Handles 100+ blueprint projects
- ✅ Works with rapid editing (10+ changes/minute)
- ✅ <1% false positives (unnecessary exports)

---

## Documentation Updates

### README.md Addition

```markdown
## 🔄 Auto-Refresh (Automatic Export)

**Run once and forget:**
```python
import sys; sys.path.append("/path/to/Content/Python")
import blueprint_watcher
blueprint_watcher.start_auto_export()
```

Your blueprints will now automatically export when you save changes!

**To stop:**
```python
blueprint_watcher.stop_auto_export()
```
```

---

## Alternatives Considered

### Option A: File System Watcher
**Rejected:** Can't monitor .uasset files effectively, platform-specific

### Option B: Blueprint Save Hook
**Rejected:** Requires C++ modification, not portable

### Option C: Editor Utility Widget
**Considered:** Good for UI, but adds setup complexity for users

**Final Choice: Asset Registry + Tick Callback**
- Native to UE5
- Works in Python
- No external dependencies
- Cross-platform

---

## Next Steps

1. **Prototype core system** (1-2 hours)
2. **Test with your project** (30 min)
3. **Refine debouncing** (1 hour)
4. **Add to repository** (30 min)
5. **Update documentation** (30 min)

**Total Time Estimate: 4-5 hours**

---

## Questions for User

1. **Debounce time:** 2 seconds okay, or prefer longer/shorter?
2. **Notifications:** Want to see "Blueprint exported" messages?
3. **Startup:** Auto-start on project open, or manual start?
4. **Scope:** Export all blueprints or just changed ones?

---

**Ready to implement? Let me know and I'll start coding the auto-refresh system!** 🚀
