import React from "react";
import ScenarioWizardModern from "../components/scenario-runner/ScenarioWizardModern";
import { useNavigate } from "react-router-dom";

export default function ScenarioEditorTest() {
  const navigate = useNavigate();

  const handleCancel = () => {
    navigate("/");
  };

  const handleComplete = () => {
    navigate("/scenario-runner");
  };

  return (
    <ScenarioWizardModern 
      onCancel={handleCancel}
      onComplete={handleComplete}
    />
  );
} 