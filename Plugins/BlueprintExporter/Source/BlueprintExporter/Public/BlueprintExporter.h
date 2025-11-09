// BlueprintExporter.h
// C++ Plugin for extracting UE5 Blueprint graph data
// Place this in: Plugins/BlueprintExporter/Source/BlueprintExporter/Public/

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Engine/Blueprint.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "EdGraph/EdGraphPin.h"
#include "BlueprintExporter.generated.h"

/**
 * Blueprint Exporter Library
 * Provides functions to extract blueprint data for Claude Code integration
 */
UCLASS()
class BLUEPRINTEXPORTER_API UBlueprintExporterLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Extract complete blueprint data as JSON string
	 * @param Blueprint - The blueprint to extract data from
	 * @return JSON string containing all blueprint information
	 */
	UFUNCTION(BlueprintCallable, Category = "Blueprint Exporter")
	static FString ExtractBlueprintData(UBlueprint* Blueprint);

	/**
	 * Get all blueprints in the project
	 * @return Array of all blueprint assets
	 */
	UFUNCTION(BlueprintCallable, Category = "Blueprint Exporter")
	static TArray<UBlueprint*> GetAllProjectBlueprints();

	/**
	 * Export blueprint to JSON file
	 * @param Blueprint - The blueprint to export
	 * @param FilePath - Output file path (absolute)
	 * @return True if export succeeded
	 */
	UFUNCTION(BlueprintCallable, Category = "Blueprint Exporter")
	static bool ExportBlueprintToFile(UBlueprint* Blueprint, const FString& FilePath);

	/**
	 * Export all project blueprints to directory
	 * @param OutputDirectory - Directory to export to
	 * @return Number of blueprints exported
	 */
	UFUNCTION(BlueprintCallable, Category = "Blueprint Exporter")
	static int32 ExportAllBlueprints(const FString& OutputDirectory);

private:
	// Internal serialization functions
	static TSharedPtr<FJsonObject> SerializeBlueprint(UBlueprint* Blueprint);
	static TSharedPtr<FJsonObject> SerializeGraph(UEdGraph* Graph);
	static TSharedPtr<FJsonObject> SerializeNode(UEdGraphNode* Node);
	static TSharedPtr<FJsonObject> SerializePin(UEdGraphPin* Pin);
	static TArray<TSharedPtr<FJsonValue>> SerializeVariables(UBlueprint* Blueprint);
	static TArray<TSharedPtr<FJsonValue>> SerializeFunctions(UBlueprint* Blueprint);
	static TArray<TSharedPtr<FJsonValue>> SerializeComponents(UBlueprint* Blueprint);
	static TArray<TSharedPtr<FJsonValue>> ExtractDependencies(UBlueprint* Blueprint);

	// Helper functions
	static FString PinTypeToString(const FEdGraphPinType& PinType);
	static FString NodeTypeToString(UEdGraphNode* Node);
	static FString GetNodeCategory(UEdGraphNode* Node);
	static TArray<UEdGraphNode*> GetConnectedNodes(UEdGraphNode* Node);
};

/**
 * Blueprint Change Monitor
 * Monitors blueprint assets for changes and triggers callbacks
 */
UCLASS()
class BLUEPRINTEXPORTER_API UBlueprintChangeMonitor : public UObject
{
	GENERATED_BODY()

public:
	DECLARE_DYNAMIC_DELEGATE_OneParam(FOnBlueprintChanged, UBlueprint*, ChangedBlueprint);

	/**
	 * Start monitoring blueprint changes
	 * @param OnChanged - Callback when blueprint changes
	 */
	UFUNCTION(BlueprintCallable, Category = "Blueprint Exporter")
	void StartMonitoring(FOnBlueprintChanged OnChanged);

	/**
	 * Stop monitoring
	 */
	UFUNCTION(BlueprintCallable, Category = "Blueprint Exporter")
	void StopMonitoring();

private:
	void OnAssetAdded(const FAssetData& AssetData);
	void OnAssetRemoved(const FAssetData& AssetData);
	void OnAssetModified(const FAssetData& AssetData);

	FOnBlueprintChanged OnBlueprintChangedDelegate;
	TMap<FString, FDateTime> BlueprintModificationTimes;
};
