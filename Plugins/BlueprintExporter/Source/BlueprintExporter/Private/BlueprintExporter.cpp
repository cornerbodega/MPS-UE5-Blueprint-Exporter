// BlueprintExporter.cpp

#include "BlueprintExporter.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "K2Node.h"
#include "K2Node_Event.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_CallFunction.h"
#include "K2Node_VariableGet.h"
#include "K2Node_VariableSet.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformFileManager.h"
#include "Engine/SimpleConstructionScript.h"
#include "Engine/SCS_Node.h"

// ============================================================================
// Main Export Functions
// ============================================================================

FString UBlueprintExporterLibrary::ExtractBlueprintData(UBlueprint* Blueprint)
{
	if (!Blueprint)
	{
		UE_LOG(LogTemp, Error, TEXT("ExtractBlueprintData: Invalid blueprint"));
		return TEXT("{}");
	}

	TSharedPtr<FJsonObject> JsonObject = SerializeBlueprint(Blueprint);

	// Convert to string
	FString OutputString;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
	FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);

	return OutputString;
}

TArray<UBlueprint*> UBlueprintExporterLibrary::GetAllProjectBlueprints()
{
	TArray<UBlueprint*> Blueprints;

	FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
	IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();

	TArray<FAssetData> AssetDataList;
	AssetRegistry.GetAssetsByClass(UBlueprint::StaticClass()->GetClassPathName(), AssetDataList);

	for (const FAssetData& AssetData : AssetDataList)
	{
		if (UBlueprint* Blueprint = Cast<UBlueprint>(AssetData.GetAsset()))
		{
			Blueprints.Add(Blueprint);
		}
	}

	return Blueprints;
}

bool UBlueprintExporterLibrary::ExportBlueprintToFile(UBlueprint* Blueprint, const FString& FilePath)
{
	if (!Blueprint)
	{
		UE_LOG(LogTemp, Error, TEXT("ExportBlueprintToFile: Invalid blueprint"));
		return false;
	}

	FString JsonString = ExtractBlueprintData(Blueprint);

	// Save to file
	if (FFileHelper::SaveStringToFile(JsonString, *FilePath))
	{
		UE_LOG(LogTemp, Log, TEXT("Exported blueprint to: %s"), *FilePath);
		return true;
	}

	UE_LOG(LogTemp, Error, TEXT("Failed to save file: %s"), *FilePath);
	return false;
}

int32 UBlueprintExporterLibrary::ExportAllBlueprints(const FString& OutputDirectory)
{
	TArray<UBlueprint*> Blueprints = GetAllProjectBlueprints();
	int32 ExportedCount = 0;

	for (UBlueprint* Blueprint : Blueprints)
	{
		FString FileName = Blueprint->GetName() + TEXT(".json");
		FString FilePath = FPaths::Combine(OutputDirectory, FileName);

		if (ExportBlueprintToFile(Blueprint, FilePath))
		{
			ExportedCount++;
		}
	}

	UE_LOG(LogTemp, Log, TEXT("Exported %d blueprints to %s"), ExportedCount, *OutputDirectory);
	return ExportedCount;
}

// ============================================================================
// Serialization Functions
// ============================================================================

TSharedPtr<FJsonObject> UBlueprintExporterLibrary::SerializeBlueprint(UBlueprint* Blueprint)
{
	TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);

	// Basic info
	JsonObject->SetStringField(TEXT("name"), Blueprint->GetName());
	JsonObject->SetStringField(TEXT("path"), Blueprint->GetPathName());
	JsonObject->SetStringField(TEXT("class_type"), TEXT("Blueprint"));

	// Parent class
	if (Blueprint->ParentClass)
	{
		JsonObject->SetStringField(TEXT("parent_class"), Blueprint->ParentClass->GetName());
	}

	// Generated class
	if (Blueprint->GeneratedClass)
	{
		JsonObject->SetStringField(TEXT("generated_class"), Blueprint->GeneratedClass->GetName());
	}

	// Graphs
	TArray<TSharedPtr<FJsonValue>> GraphsArray;
	for (UEdGraph* Graph : Blueprint->UbergraphPages)
	{
		if (Graph)
		{
			GraphsArray.Add(MakeShareable(new FJsonValueObject(SerializeGraph(Graph))));
		}
	}

	// Also add function graphs
	for (UEdGraph* Graph : Blueprint->FunctionGraphs)
	{
		if (Graph)
		{
			GraphsArray.Add(MakeShareable(new FJsonValueObject(SerializeGraph(Graph))));
		}
	}

	JsonObject->SetArrayField(TEXT("graphs"), GraphsArray);

	// Variables
	JsonObject->SetArrayField(TEXT("variables"), SerializeVariables(Blueprint));

	// Functions
	JsonObject->SetArrayField(TEXT("functions"), SerializeFunctions(Blueprint));

	// Components
	JsonObject->SetArrayField(TEXT("components"), SerializeComponents(Blueprint));

	// Dependencies
	JsonObject->SetArrayField(TEXT("dependencies"), ExtractDependencies(Blueprint));

	return JsonObject;
}

TSharedPtr<FJsonObject> UBlueprintExporterLibrary::SerializeGraph(UEdGraph* Graph)
{
	TSharedPtr<FJsonObject> GraphObject = MakeShareable(new FJsonObject);

	GraphObject->SetStringField(TEXT("name"), Graph->GetName());

	// Serialize nodes
	TArray<TSharedPtr<FJsonValue>> NodesArray;
	for (UEdGraphNode* Node : Graph->Nodes)
	{
		if (Node)
		{
			NodesArray.Add(MakeShareable(new FJsonValueObject(SerializeNode(Node))));
		}
	}

	GraphObject->SetArrayField(TEXT("nodes"), NodesArray);

	return GraphObject;
}

TSharedPtr<FJsonObject> UBlueprintExporterLibrary::SerializeNode(UEdGraphNode* Node)
{
	TSharedPtr<FJsonObject> NodeObject = MakeShareable(new FJsonObject);

	NodeObject->SetStringField(TEXT("id"), Node->GetName());
	NodeObject->SetStringField(TEXT("type"), NodeTypeToString(Node));
	NodeObject->SetStringField(TEXT("title"), Node->GetNodeTitle(ENodeTitleType::FullTitle).ToString());
	NodeObject->SetStringField(TEXT("category"), GetNodeCategory(Node));

	// Position
	TSharedPtr<FJsonObject> PosObject = MakeShareable(new FJsonObject);
	PosObject->SetNumberField(TEXT("x"), Node->NodePosX);
	PosObject->SetNumberField(TEXT("y"), Node->NodePosY);
	NodeObject->SetObjectField(TEXT("position"), PosObject);

	// Pins
	TArray<TSharedPtr<FJsonValue>> PinsArray;
	for (UEdGraphPin* Pin : Node->Pins)
	{
		if (Pin)
		{
			PinsArray.Add(MakeShareable(new FJsonValueObject(SerializePin(Pin))));
		}
	}
	NodeObject->SetArrayField(TEXT("pins"), PinsArray);

	// Connected nodes
	TArray<TSharedPtr<FJsonValue>> ConnectionsArray;
	TArray<UEdGraphNode*> ConnectedNodes = GetConnectedNodes(Node);
	for (UEdGraphNode* ConnectedNode : ConnectedNodes)
	{
		ConnectionsArray.Add(MakeShareable(new FJsonValueString(ConnectedNode->GetName())));
	}
	NodeObject->SetArrayField(TEXT("connections"), ConnectionsArray);

	return NodeObject;
}

TSharedPtr<FJsonObject> UBlueprintExporterLibrary::SerializePin(UEdGraphPin* Pin)
{
	TSharedPtr<FJsonObject> PinObject = MakeShareable(new FJsonObject);

	PinObject->SetStringField(TEXT("name"), Pin->GetName());
	PinObject->SetStringField(TEXT("display_name"), Pin->GetDisplayName().ToString());
	PinObject->SetStringField(TEXT("direction"), Pin->Direction == EGPD_Input ? TEXT("input") : TEXT("output"));
	PinObject->SetStringField(TEXT("type"), PinTypeToString(Pin->PinType));

	// Default value
	if (!Pin->DefaultValue.IsEmpty())
	{
		PinObject->SetStringField(TEXT("default_value"), Pin->DefaultValue);
	}

	return PinObject;
}

TArray<TSharedPtr<FJsonValue>> UBlueprintExporterLibrary::SerializeVariables(UBlueprint* Blueprint)
{
	TArray<TSharedPtr<FJsonValue>> VariablesArray;

	for (const FBPVariableDescription& Variable : Blueprint->NewVariables)
	{
		TSharedPtr<FJsonObject> VarObject = MakeShareable(new FJsonObject);

		VarObject->SetStringField(TEXT("name"), Variable.VarName.ToString());
		VarObject->SetStringField(TEXT("type"), PinTypeToString(Variable.VarType));
		VarObject->SetStringField(TEXT("category"), Variable.Category.ToString());
		VarObject->SetBoolField(TEXT("is_exposed"), (Variable.PropertyFlags & CPF_ExposeOnSpawn) != 0);

		// Default value
		if (!Variable.DefaultValue.IsEmpty())
		{
			VarObject->SetStringField(TEXT("default_value"), Variable.DefaultValue);
		}

		VariablesArray.Add(MakeShareable(new FJsonValueObject(VarObject)));
	}

	return VariablesArray;
}

TArray<TSharedPtr<FJsonValue>> UBlueprintExporterLibrary::SerializeFunctions(UBlueprint* Blueprint)
{
	TArray<TSharedPtr<FJsonValue>> FunctionsArray;

	for (UEdGraph* FunctionGraph : Blueprint->FunctionGraphs)
	{
		if (!FunctionGraph) continue;

		TSharedPtr<FJsonObject> FuncObject = MakeShareable(new FJsonObject);

		FuncObject->SetStringField(TEXT("name"), FunctionGraph->GetName());

		// Find function entry node to get parameters
		TArray<TSharedPtr<FJsonValue>> ParamsArray;
		for (UEdGraphNode* Node : FunctionGraph->Nodes)
		{
			if (UK2Node_FunctionEntry* EntryNode = Cast<UK2Node_FunctionEntry>(Node))
			{
				for (UEdGraphPin* Pin : EntryNode->Pins)
				{
					if (Pin && Pin->Direction == EGPD_Output && Pin->PinType.PinCategory != UEdGraphSchema_K2::PC_Exec)
					{
						TSharedPtr<FJsonObject> ParamObject = MakeShareable(new FJsonObject);
						ParamObject->SetStringField(TEXT("name"), Pin->GetName());
						ParamObject->SetStringField(TEXT("type"), PinTypeToString(Pin->PinType));
						ParamsArray.Add(MakeShareable(new FJsonValueObject(ParamObject)));
					}
				}
			}
		}

		FuncObject->SetArrayField(TEXT("parameters"), ParamsArray);

		// Include the graph structure
		FuncObject->SetObjectField(TEXT("graph"), SerializeGraph(FunctionGraph));

		FunctionsArray.Add(MakeShareable(new FJsonValueObject(FuncObject)));
	}

	return FunctionsArray;
}

TArray<TSharedPtr<FJsonValue>> UBlueprintExporterLibrary::SerializeComponents(UBlueprint* Blueprint)
{
	TArray<TSharedPtr<FJsonValue>> ComponentsArray;

	// Get components from SimpleConstructionScript
	if (Blueprint->SimpleConstructionScript)
	{
		const TArray<USCS_Node*>& Nodes = Blueprint->SimpleConstructionScript->GetAllNodes();

		for (USCS_Node* Node : Nodes)
		{
			if (Node && Node->ComponentTemplate)
			{
				TSharedPtr<FJsonObject> CompObject = MakeShareable(new FJsonObject);

				CompObject->SetStringField(TEXT("name"), Node->GetVariableName().ToString());
				CompObject->SetStringField(TEXT("class"), Node->ComponentTemplate->GetClass()->GetName());

				ComponentsArray.Add(MakeShareable(new FJsonValueObject(CompObject)));
			}
		}
	}

	return ComponentsArray;
}

TArray<TSharedPtr<FJsonValue>> UBlueprintExporterLibrary::ExtractDependencies(UBlueprint* Blueprint)
{
	TArray<TSharedPtr<FJsonValue>> DependenciesArray;
	TSet<FString> UniqueDependencies;

	// Search through all graphs for referenced assets
	for (UEdGraph* Graph : Blueprint->UbergraphPages)
	{
		if (!Graph) continue;

		for (UEdGraphNode* Node : Graph->Nodes)
		{
			if (!Node) continue;

			// Check for function calls
			if (UK2Node_CallFunction* CallNode = Cast<UK2Node_CallFunction>(Node))
			{
				if (UClass* FunctionClass = CallNode->FunctionReference.GetMemberParentClass())
				{
					FString ClassPath = FunctionClass->GetPathName();
					if (!ClassPath.IsEmpty() && !UniqueDependencies.Contains(ClassPath))
					{
						UniqueDependencies.Add(ClassPath);
						DependenciesArray.Add(MakeShareable(new FJsonValueString(ClassPath)));
					}
				}
			}

			// Check pins for object references
			for (UEdGraphPin* Pin : Node->Pins)
			{
				if (Pin && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Object)
				{
					if (UObject* DefaultObject = Pin->DefaultObject)
					{
						FString ObjectPath = DefaultObject->GetPathName();
						if (!ObjectPath.IsEmpty() && !UniqueDependencies.Contains(ObjectPath))
						{
							UniqueDependencies.Add(ObjectPath);
							DependenciesArray.Add(MakeShareable(new FJsonValueString(ObjectPath)));
						}
					}
				}
			}
		}
	}

	return DependenciesArray;
}

// ============================================================================
// Helper Functions
// ============================================================================

FString UBlueprintExporterLibrary::PinTypeToString(const FEdGraphPinType& PinType)
{
	FString TypeString = PinType.PinCategory.ToString();

	if (PinType.PinSubCategoryObject.IsValid())
	{
		TypeString += TEXT("<") + PinType.PinSubCategoryObject->GetName() + TEXT(">");
	}

	if (PinType.IsArray())
	{
		TypeString = TEXT("Array<") + TypeString + TEXT(">");
	}

	return TypeString;
}

FString UBlueprintExporterLibrary::NodeTypeToString(UEdGraphNode* Node)
{
	if (!Node) return TEXT("Unknown");

	if (Cast<UK2Node_Event>(Node)) return TEXT("Event");
	if (Cast<UK2Node_FunctionEntry>(Node)) return TEXT("FunctionEntry");
	if (Cast<UK2Node_CallFunction>(Node)) return TEXT("CallFunction");
	if (Cast<UK2Node_VariableGet>(Node)) return TEXT("VariableGet");
	if (Cast<UK2Node_VariableSet>(Node)) return TEXT("VariableSet");

	return Node->GetClass()->GetName();
}

FString UBlueprintExporterLibrary::GetNodeCategory(UEdGraphNode* Node)
{
	if (UK2Node* K2Node = Cast<UK2Node>(Node))
	{
		return K2Node->GetMenuCategory().ToString();
	}

	return TEXT("");
}

TArray<UEdGraphNode*> UBlueprintExporterLibrary::GetConnectedNodes(UEdGraphNode* Node)
{
	TArray<UEdGraphNode*> ConnectedNodes;

	for (UEdGraphPin* Pin : Node->Pins)
	{
		if (Pin && Pin->Direction == EGPD_Output)
		{
			for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
			{
				if (LinkedPin && LinkedPin->GetOwningNode())
				{
					ConnectedNodes.AddUnique(LinkedPin->GetOwningNode());
				}
			}
		}
	}

	return ConnectedNodes;
}

// ============================================================================
// Blueprint Change Monitor Implementation
// ============================================================================

void UBlueprintChangeMonitor::StartMonitoring(FOnBlueprintChanged OnChanged)
{
	OnBlueprintChangedDelegate = OnChanged;

	FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
	IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();

	AssetRegistry.OnAssetAdded().AddUObject(this, &UBlueprintChangeMonitor::OnAssetAdded);
	AssetRegistry.OnAssetRemoved().AddUObject(this, &UBlueprintChangeMonitor::OnAssetRemoved);
	AssetRegistry.OnAssetUpdated().AddUObject(this, &UBlueprintChangeMonitor::OnAssetModified);

	UE_LOG(LogTemp, Log, TEXT("Blueprint change monitoring started"));
}

void UBlueprintChangeMonitor::StopMonitoring()
{
	FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
	IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();

	AssetRegistry.OnAssetAdded().RemoveAll(this);
	AssetRegistry.OnAssetRemoved().RemoveAll(this);
	AssetRegistry.OnAssetUpdated().RemoveAll(this);

	UE_LOG(LogTemp, Log, TEXT("Blueprint change monitoring stopped"));
}

void UBlueprintChangeMonitor::OnAssetAdded(const FAssetData& AssetData)
{
	if (AssetData.AssetClassPath == UBlueprint::StaticClass()->GetClassPathName())
	{
		if (UBlueprint* Blueprint = Cast<UBlueprint>(AssetData.GetAsset()))
		{
			OnBlueprintChangedDelegate.ExecuteIfBound(Blueprint);
		}
	}
}

void UBlueprintChangeMonitor::OnAssetRemoved(const FAssetData& AssetData)
{
	// Handle blueprint removal if needed
}

void UBlueprintChangeMonitor::OnAssetModified(const FAssetData& AssetData)
{
	if (AssetData.AssetClassPath == UBlueprint::StaticClass()->GetClassPathName())
	{
		if (UBlueprint* Blueprint = Cast<UBlueprint>(AssetData.GetAsset()))
		{
			OnBlueprintChangedDelegate.ExecuteIfBound(Blueprint);
		}
	}
}
