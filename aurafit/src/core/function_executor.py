"""
Function executor for handling LLM tool calls
Parses and executes the log_disaster_incident function
"""

import logging
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class HazardEnum:
    """Enum for valid hazard types"""
    VALID_HAZARDS = {
        "SUBMERGED_POWER_LINE",
        "GAS_LEAK",
        "UNSTABLE_STRUCTURE",
        "CHEMICAL_SPILL",
        "RAGING_FIRE",
        "FLOODING",
        "DEBRIS",
        "TOXIC_FUMES",
        "STRUCTURAL_COLLAPSE",
        "LANDSLIDE",
        "ELECTRICAL_HAZARD",
        "CRUSH_HAZARD",
        "CONTAMINATED_WATER",
        "FIRE",
        "UNKNOWN"
    }


class DisasterIncidentSchema(BaseModel):
    """Pydantic schema for disaster incident validation"""
    incident_type: str = Field(..., description="Type of disaster")
    incident_priority: str = Field(..., description="START triage priority")
    casualty_count_estimate: int = Field(default=0, ge=0, description="Number of casualties")
    hazards_detected: list = Field(default_factory=list, description="List of hazards")
    recommended_actions: list = Field(default_factory=list, description="List of actions")
    evacuation_required: bool = Field(default=False, description="Evacuation needed?")
    emergency_services_required: list = Field(default_factory=list, description="Required services")
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score")
    location_description: str = Field(default="Unknown", description="Location info")
    medical_summary: str = Field(default="", description="Medical details")
    victim_calm_response: str = Field(default="", description="Calm comforting message for victim in danger")
    communication_language: str = Field(default="English", description="Language used by victim")
    latitude: Optional[float] = Field(default=None, description="GPS Latitude")
    longitude: Optional[float] = Field(default=None, description="GPS Longitude")
    gps_coordinates: Optional[str] = Field(default=None, description="Formatted GPS coordinates")

    class Config:
        validate_assignment = True


class FunctionExecutor:
    """Handles execution of LLM function calls"""

    @staticmethod
    def validate_and_execute(function_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and execute function call from LLM
        
        Args:
            function_data: Function parameters from LLM
            
        Returns:
            Validated incident data or fallback data if validation fails
        """
        try:
            # Validate required fields
            if not function_data or not isinstance(function_data, dict):
                logger.warning("Invalid function data format")
                return FunctionExecutor._get_fallback_data()
            
            # Normalize and validate
            incident = FunctionExecutor._normalize_incident_data(function_data)
            
            # Perform validation
            validated = DisasterIncidentSchema(**incident)
            
            logger.info(f"Function validated: {validated.incident_type} - {validated.incident_priority}")
            return validated.dict()
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            # Use fallback with available data
            return FunctionExecutor._merge_with_fallback(function_data)
        except Exception as e:
            logger.error(f"Error executing function: {e}")
            return FunctionExecutor._get_fallback_data()

    @staticmethod
    def _normalize_incident_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize incident data to match schema
        
        Args:
            data: Raw incident data from LLM
            
        Returns:
            Normalized data
        """
        normalized = {}
        
        # Filter out schema-related fields (type_, description, etc.) from API response
        # Only keep the actual parameter values
        valid_fields = {
            "incident_type",
            "incident_priority",
            "casualty_count_estimate",
            "hazards_detected",
            "recommended_actions",
            "evacuation_required",
            "emergency_services_required",
            "confidence_score",
            "location_description",
            "medical_summary",
            "victim_calm_response",
            "communication_language",
            "latitude",
            "longitude",
            "gps_coordinates"
        }
        
        # Clean data - only use valid fields
        cleaned_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # Incident type validation
        incident_type = cleaned_data.get("incident_type", "OTHER")
        valid_types = {"FLOOD", "BUILDING_COLLAPSE", "FIRE_OUTBREAK", "ROAD_ACCIDENT", 
                      "GAS_EXPLOSION", "LANDSLIDE", "STORM_DAMAGE", "MEDICAL_EMERGENCY", "OTHER"}
        normalized["incident_type"] = incident_type if incident_type in valid_types else "OTHER"
        
        # Priority validation
        priority = cleaned_data.get("incident_priority", "YELLOW_DELAYED")
        valid_priorities = {"RED_IMMEDIATE", "YELLOW_DELAYED", "GREEN_MINOR", "BLACK_EXPECTANT"}
        normalized["incident_priority"] = priority if priority in valid_priorities else "YELLOW_DELAYED"
        
        # Casualty count
        try:
            casualty_count = int(cleaned_data.get("casualty_count_estimate", 0))
            normalized["casualty_count_estimate"] = max(0, casualty_count)
        except (ValueError, TypeError):
            normalized["casualty_count_estimate"] = 0
        
        # Hazards - ensure it's a list
        hazards = cleaned_data.get("hazards_detected", [])
        if isinstance(hazards, str):
            hazards = [hazards]
        elif not isinstance(hazards, list):
            hazards = []
        normalized["hazards_detected"] = [str(h).upper() for h in hazards]
        
        # Actions - ensure it's a list
        actions = cleaned_data.get("recommended_actions", [])
        if isinstance(actions, str):
            actions = [actions]
        elif not isinstance(actions, list):
            actions = []
        normalized["recommended_actions"] = [str(a) for a in actions]
        
        # Evacuation
        evacuation = cleaned_data.get("evacuation_required", False)
        normalized["evacuation_required"] = bool(evacuation)
        
        # Emergency services - ensure it's a list
        services = cleaned_data.get("emergency_services_required", [])
        if isinstance(services, str):
            services = [services]
        elif not isinstance(services, list):
            services = []
        normalized["emergency_services_required"] = [str(s).upper() for s in services]
        
        # Confidence score
        try:
            confidence = float(cleaned_data.get("confidence_score", 0.5))
            normalized["confidence_score"] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            normalized["confidence_score"] = 0.5
        
        # Location and medical summary
        normalized["location_description"] = str(cleaned_data.get("location_description", "Unknown"))
        normalized["medical_summary"] = str(cleaned_data.get("medical_summary", ""))
        normalized["victim_calm_response"] = str(cleaned_data.get("victim_calm_response", ""))
        normalized["communication_language"] = str(cleaned_data.get("communication_language", "English"))
        
        # GPS coordinates parsing
        lat = cleaned_data.get("latitude")
        lon = cleaned_data.get("longitude")
        if lat is not None:
            try:
                normalized["latitude"] = float(lat)
            except (ValueError, TypeError):
                normalized["latitude"] = None
        else:
            normalized["latitude"] = None
            
        if lon is not None:
            try:
                normalized["longitude"] = float(lon)
            except (ValueError, TypeError):
                normalized["longitude"] = None
        else:
            normalized["longitude"] = None

        if cleaned_data.get("gps_coordinates"):
            normalized["gps_coordinates"] = str(cleaned_data.get("gps_coordinates"))
        elif normalized["latitude"] is not None and normalized["longitude"] is not None:
            normalized["gps_coordinates"] = f"{normalized['latitude']:.5f}, {normalized['longitude']:.5f}"
        else:
            normalized["gps_coordinates"] = None

        return normalized

    @staticmethod
    def _get_fallback_data() -> Dict[str, Any]:
        """
        Get fallback data when parsing fails
        
        Returns:
            Safe default incident data
        """
        return {
            "incident_type": "OTHER",
            "incident_priority": "YELLOW_DELAYED",
            "casualty_count_estimate": 0,
            "hazards_detected": ["UNKNOWN"],
            "recommended_actions": [
                "Stay calm and move to a safe place if you can.",
                "Keep away from damaged structures or water.",
                "Wait for emergency rescue teams to arrive."
            ],
            "evacuation_required": False,
            "emergency_services_required": ["EMERGENCY_RESPONSE"],
            "confidence_score": 0.3,
            "location_description": "Location not specified",
            "medical_summary": "Status unknown - awaiting assessment",
            "victim_calm_response": "No panic my friend, help is on the way. Make you stay in a safe place.",
            "communication_language": "English"
        }

    @staticmethod
    def _merge_with_fallback(function_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge partially valid data with fallback values
        
        Args:
            function_data: Partially valid incident data
            
        Returns:
            Merged incident data
        """
        fallback = FunctionExecutor._get_fallback_data()
        merged = fallback.copy()
        
        # Keep valid values from function_data
        if "incident_type" in function_data and function_data["incident_type"]:
            merged["incident_type"] = str(function_data["incident_type"])
        
        if "incident_priority" in function_data and function_data["incident_priority"]:
            merged["incident_priority"] = str(function_data["incident_priority"])
        
        if "casualty_count_estimate" in function_data:
            try:
                merged["casualty_count_estimate"] = int(function_data["casualty_count_estimate"])
            except (ValueError, TypeError):
                pass
        
        if "hazards_detected" in function_data and function_data["hazards_detected"]:
            merged["hazards_detected"] = function_data["hazards_detected"]
        
        if "recommended_actions" in function_data and function_data["recommended_actions"]:
            merged["recommended_actions"] = function_data["recommended_actions"]
        
        if "location_description" in function_data and function_data["location_description"]:
            merged["location_description"] = str(function_data["location_description"])
        
        if "victim_calm_response" in function_data and function_data["victim_calm_response"]:
            merged["victim_calm_response"] = str(function_data["victim_calm_response"])

        if "communication_language" in function_data and function_data["communication_language"]:
            merged["communication_language"] = str(function_data["communication_language"])

        if "latitude" in function_data and function_data["latitude"] is not None:
            merged["latitude"] = function_data["latitude"]

        if "longitude" in function_data and function_data["longitude"] is not None:
            merged["longitude"] = function_data["longitude"]

        if "gps_coordinates" in function_data and function_data["gps_coordinates"]:
            merged["gps_coordinates"] = str(function_data["gps_coordinates"])
        
        return merged


def parse_function_call(response_text: str, function_call_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse LLM response and extract function call or JSON text response
    
    Args:
        response_text: Text response from LLM
        function_call_data: Structured function call data
        
    Returns:
        Validated incident data or None
    """
    try:
        if function_call_data and isinstance(function_call_data, dict):
            # Use structured function call
            return FunctionExecutor.validate_and_execute(function_call_data)
        elif response_text:
            # Try parsing response_text as JSON
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    return FunctionExecutor.validate_and_execute(data)
            except json.JSONDecodeError:
                logger.warning("Failed to decode JSON from text response, using fallback merge")
                
            return FunctionExecutor._get_fallback_data()
        else:
            logger.warning("Using fallback for function parsing")
            return FunctionExecutor._get_fallback_data()
            
    except Exception as e:
        logger.error(f"Error parsing function call: {e}")
        return FunctionExecutor._get_fallback_data()
