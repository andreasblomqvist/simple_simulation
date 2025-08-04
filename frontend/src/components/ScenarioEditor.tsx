import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { Slider } from "../components/ui/slider";
import { Tooltip, TooltipContent, TooltipTrigger } from "../components/ui/tooltip";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "../components/ui/dialog";
import { Info } from "lucide-react";

const leverInfo = {
  recruitment: "Controls the rate of new hires for this scenario.",
  churn: "Represents the percentage of employees leaving.",
  progression: "Adjusts how quickly employees move up levels."
};

export function ScenarioEditor() {
  const [name, setName] = useState("Scenario A");
  const [description, setDescription] = useState("");
  const [levers, setLevers] = useState({
    recruitment: 10,
    churn: 5,
    progression: 20
  });
  const [showSummary, setShowSummary] = useState(false);

  const handleLeverChange = (key: keyof typeof levers, value: number) => {
    setLevers((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => setShowSummary(true);
  const handleConfirmSave = () => {
    setShowSummary(false);
    // Save logic here
  };

  return (
    <form className="max-w-xl mx-auto space-y-6 pb-32">
      {/* Scenario Name & Description */}
      <Card>
        <CardHeader>
          <CardTitle>Edit Scenario</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter scenario name"
          />
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe this scenario"
          />
        </CardContent>
      </Card>

      {/* Levers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(levers).map(([key, value]) => (
          <Card key={key}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="capitalize">{key}</CardTitle>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground cursor-pointer" />
                </TooltipTrigger>
                <TooltipContent>{leverInfo[key as keyof typeof levers]}</TooltipContent>
              </Tooltip>
            </CardHeader>
            <CardContent>
              <Slider
                min={0}
                max={100}
                step={1}
                value={[value]}
                onValueChange={([v]) => handleLeverChange(key as keyof typeof levers, v)}
              />
              <div className="text-right text-sm mt-2">{value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Sticky Footer */}
      <div className="fixed bottom-0 left-0 w-full bg-background border-t border-border p-4 flex justify-end gap-2 z-50">
        <Button variant="outline" type="button" onClick={() => {/* cancel logic */}}>Cancel</Button>
        <Button type="button" onClick={handleSave}>Save</Button>
      </div>

      {/* Modal Summary */}
      <Dialog open={showSummary} onOpenChange={setShowSummary}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Changes</DialogTitle>
          </DialogHeader>
          <div>
            <div className="mb-2 font-semibold">Scenario Name:</div>
            <div className="mb-4">{name}</div>
            <div className="mb-2 font-semibold">Description:</div>
            <div className="mb-4">{description}</div>
            <div className="mb-2 font-semibold">Levers:</div>
            <ul className="list-disc pl-5">
              {Object.entries(levers).map(([key, value]) => (
                <li key={key} className="capitalize">{key}: {value}</li>
              ))}
            </ul>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setShowSummary(false)}>Back</Button>
            <Button type="button" onClick={handleConfirmSave}>Confirm Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </form>
  );
} 