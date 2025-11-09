// BlueprintExporter.Build.cs

using UnrealBuildTool;

public class BlueprintExporter : ModuleRules
{
	public BlueprintExporter(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject",
				"Engine",
				"UnrealEd",
				"BlueprintGraph",
				"Kismet",
				"KismetCompiler",
				"GraphEditor",
				"Json",
				"JsonUtilities",
				"AssetRegistry",
				"EditorSubsystem"
			}
		);

		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"Slate",
				"SlateCore",
				"InputCore",
				"PropertyEditor",
				"LevelEditor",
				"Projects"
			}
		);
	}
}
