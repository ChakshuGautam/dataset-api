import { useState } from "react";
import { AnalysisResults } from "./components/AnalysisResults";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Sparkles, FileText, Database } from "lucide-react";
import type { AnalysisResult } from "./types/analysis";

// Import the static data
import schemaData from "./assets/schema.json";
import analysisData from "./assets/data.json";

function App() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult>(analysisData);

  const handleResultChange = (newResult: AnalysisResult) => {
    setAnalysisResult(newResult);
  };

  const renderSchemaProperty = (key: string, property: any, level = 0) => {
    const indent = level * 20;
    
    if (property.type === 'object' && property.properties) {
      return (
        <div key={key} style={{ marginLeft: indent }} className="mb-3">
          <div className="font-semibold text-blue-700 text-sm">
            {key}: {property.type}
          </div>
          {property.description && (
            <div className="text-xs text-gray-600 mb-2">{property.description}</div>
          )}
          <div className="border-l-2 border-gray-200 pl-3">
            {Object.entries(property.properties).map(([subKey, subProp]) =>
              renderSchemaProperty(subKey, subProp, level + 1)
            )}
          </div>
        </div>
      );
    }
    
    if (property.type === 'array') {
      return (
        <div key={key} style={{ marginLeft: indent }} className="mb-2">
          <div className="font-medium text-green-700 text-sm">
            {key}: {property.type}
            {property.items?.type && ` of ${property.items.type}`}
          </div>
          {property.description && (
            <div className="text-xs text-gray-600">{property.description}</div>
          )}
          {property.minItems && (
            <div className="text-xs text-gray-500">Min items: {property.minItems}</div>
          )}
        </div>
      );
    }
    
    return (
      <div key={key} style={{ marginLeft: indent }} className="mb-2">
        <div className="font-medium text-purple-700 text-sm">
          {key}: {property.type}
          {property.pattern && <span className="text-gray-500"> (pattern: {property.pattern})</span>}
        </div>
        {property.description && (
          <div className="text-xs text-gray-600">{property.description}</div>
        )}
        {property.minLength && (
          <div className="text-xs text-gray-500">Min length: {property.minLength}</div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold text-gray-900">
              Schema & Data Viewer
            </h1>
          </div>
          <p className="text-lg text-gray-600">
            View the JSON schema structure alongside the actual data
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
          {/* Left Column - Schema */}
          <div className="space-y-6">
            <Card className="h-fit">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  <CardTitle>JSON Schema</CardTitle>
                </div>
                <CardDescription>
                  Structure and validation rules for the data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-[calc(100vh-300px)] overflow-y-auto">
                  <div className="mb-4">
                    <div className="font-bold text-lg text-gray-800 mb-2">
                      {schemaData.title}
                    </div>
                    <div className="text-sm text-gray-600 mb-4">
                      {schemaData.description}
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="font-semibold text-gray-700 border-b pb-2">Properties:</div>
                    {Object.entries(schemaData.properties).map(([key, property]) =>
                      renderSchemaProperty(key, property)
                    )}
                  </div>
                  
                  {schemaData.required && (
                    <div className="mt-4 pt-4 border-t">
                      <div className="font-semibold text-red-700 mb-2">Required Fields:</div>
                      <div className="flex flex-wrap gap-2">
                        {schemaData.required.map((field: string) => (
                          <span key={field} className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">
                            {field}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Data */}
          <div className="space-y-6">
            <Card className="h-fit">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  <CardTitle>Analysis Data</CardTitle>
                </div>
                <CardDescription>
                  Actual data that conforms to the schema
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-[calc(100vh-300px)] overflow-y-auto">
                  <AnalysisResults
                    result={analysisResult}
                    onResultChange={handleResultChange}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-16 pt-8 border-t border-gray-200">
        <p className="text-center text-sm text-gray-500">
          Schema-driven data viewer for children's literature analysis
        </p>
      </div>
    </div>
  );
}

export default App;
