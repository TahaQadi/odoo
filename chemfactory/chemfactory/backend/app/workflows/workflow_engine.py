"""
Flexible Workflow Engine for ChemFactory MES/ERP
Provides dynamic process automation and workflow management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

@dataclass
class Task:
    id: str
    name: str
    type: str
    status: TaskStatus
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    data: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class WorkflowDefinition:
    id: str
    name: str
    description: str
    version: str
    status: WorkflowStatus
    tasks: List[Task]
    connections: List[Dict[str, str]]  # from_task_id -> to_task_id
    conditions: Dict[str, str]  # task_id -> condition_expression
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class WorkflowInstance:
    id: str
    workflow_definition_id: str
    status: WorkflowStatus
    current_tasks: List[str]
    completed_tasks: List[str]
    data: Dict[str, Any]
    started_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.utcnow()

class WorkflowEngine:
    """Flexible workflow engine for process automation"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.workflow_definitions = {}
        self.active_instances = {}
        self.task_handlers = {}
    
    def register_task_handler(self, task_type: str, handler_func):
        """Register a handler function for a specific task type"""
        self.task_handlers[task_type] = handler_func
    
    def create_workflow_definition(self, definition_data: Dict) -> WorkflowDefinition:
        """Create a new workflow definition"""
        try:
            workflow_id = definition_data.get('id', f"wf_{datetime.utcnow().timestamp()}")
            
            # Parse tasks
            tasks = []
            for task_data in definition_data.get('tasks', []):
                task = Task(
                    id=task_data['id'],
                    name=task_data['name'],
                    type=task_data['type'],
                    status=TaskStatus.PENDING,
                    assignee=task_data.get('assignee'),
                    due_date=task_data.get('due_date'),
                    data=task_data.get('data', {})
                )
                tasks.append(task)
            
            workflow = WorkflowDefinition(
                id=workflow_id,
                name=definition_data['name'],
                description=definition_data.get('description', ''),
                version=definition_data.get('version', '1.0'),
                status=WorkflowStatus.DRAFT,
                tasks=tasks,
                connections=definition_data.get('connections', []),
                conditions=definition_data.get('conditions', {})
            )
            
            self.workflow_definitions[workflow_id] = workflow
            return workflow
            
        except Exception as e:
            logger.error(f"Error creating workflow definition: {e}")
            raise
    
    def start_workflow(self, workflow_id: str, initial_data: Dict = None) -> WorkflowInstance:
        """Start a new workflow instance"""
        try:
            if workflow_id not in self.workflow_definitions:
                raise ValueError(f"Workflow definition {workflow_id} not found")
            
            definition = self.workflow_definitions[workflow_id]
            
            # Create workflow instance
            instance_id = f"inst_{datetime.utcnow().timestamp()}"
            instance = WorkflowInstance(
                id=instance_id,
                workflow_definition_id=workflow_id,
                status=WorkflowStatus.ACTIVE,
                current_tasks=[],
                completed_tasks=[],
                data=initial_data or {}
            )
            
            # Find starting tasks (tasks with no incoming connections)
            all_task_ids = {task.id for task in definition.tasks}
            connected_tasks = {conn['to'] for conn in definition.connections}
            starting_tasks = list(all_task_ids - connected_tasks)
            
            instance.current_tasks = starting_tasks
            self.active_instances[instance_id] = instance
            
            # Start initial tasks
            for task_id in starting_tasks:
                self._execute_task(instance_id, task_id)
            
            return instance
            
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            raise
    
    def _execute_task(self, instance_id: str, task_id: str):
        """Execute a specific task in a workflow instance"""
        try:
            instance = self.active_instances[instance_id]
            definition = self.workflow_definitions[instance.workflow_definition_id]
            
            # Find the task
            task = next((t for t in definition.tasks if t.id == task_id), None)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.utcnow()
            
            # Execute task based on type
            if task.type in self.task_handlers:
                handler = self.task_handlers[task.type]
                result = handler(task, instance.data)
                
                if result.get('success', False):
                    task.status = TaskStatus.COMPLETED
                    instance.completed_tasks.append(task_id)
                    instance.current_tasks.remove(task_id)
                    
                    # Move to next tasks
                    self._move_to_next_tasks(instance_id, task_id)
                else:
                    task.status = TaskStatus.FAILED
                    logger.error(f"Task {task_id} failed: {result.get('error', 'Unknown error')}")
            else:
                # Default task execution
                task.status = TaskStatus.COMPLETED
                instance.completed_tasks.append(task_id)
                instance.current_tasks.remove(task_id)
                self._move_to_next_tasks(instance_id, task_id)
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            if instance_id in self.active_instances:
                task = next((t for t in definition.tasks if t.id == task_id), None)
                if task:
                    task.status = TaskStatus.FAILED
    
    def _move_to_next_tasks(self, instance_id: str, completed_task_id: str):
        """Move to next tasks after completing a task"""
        try:
            instance = self.active_instances[instance_id]
            definition = self.workflow_definitions[instance.workflow_definition_id]
            
            # Find next tasks
            next_tasks = []
            for connection in definition.connections:
                if connection['from'] == completed_task_id:
                    next_task_id = connection['to']
                    
                    # Check if all prerequisites are completed
                    if self._check_prerequisites(instance_id, next_task_id):
                        next_tasks.append(next_task_id)
            
            # Add next tasks to current tasks
            instance.current_tasks.extend(next_tasks)
            
            # Execute next tasks
            for task_id in next_tasks:
                self._execute_task(instance_id, task_id)
            
            # Check if workflow is complete
            if not instance.current_tasks:
                instance.status = WorkflowStatus.COMPLETED
                instance.completed_at = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Error moving to next tasks: {e}")
    
    def _check_prerequisites(self, instance_id: str, task_id: str) -> bool:
        """Check if all prerequisites for a task are completed"""
        instance = self.active_instances[instance_id]
        definition = self.workflow_definitions[instance.workflow_definition_id]
        
        # Find all tasks that should be completed before this task
        prerequisite_tasks = []
        for connection in definition.connections:
            if connection['to'] == task_id:
                prerequisite_tasks.append(connection['from'])
        
        # Check if all prerequisites are completed
        return all(prereq in instance.completed_tasks for prereq in prerequisite_tasks)
    
    def get_workflow_status(self, instance_id: str) -> Dict:
        """Get current status of a workflow instance"""
        if instance_id not in self.active_instances:
            return {"error": "Workflow instance not found"}
        
        instance = self.active_instances[instance_id]
        definition = self.workflow_definitions[instance.workflow_definition_id]
        
        return {
            "instance_id": instance_id,
            "workflow_name": definition.name,
            "status": instance.status.value,
            "current_tasks": instance.current_tasks,
            "completed_tasks": instance.completed_tasks,
            "progress": len(instance.completed_tasks) / len(definition.tasks) * 100,
            "started_at": instance.started_at.isoformat(),
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None
        }
    
    def pause_workflow(self, instance_id: str) -> bool:
        """Pause a workflow instance"""
        if instance_id in self.active_instances:
            self.active_instances[instance_id].status = WorkflowStatus.PAUSED
            return True
        return False
    
    def resume_workflow(self, instance_id: str) -> bool:
        """Resume a paused workflow instance"""
        if instance_id in self.active_instances:
            self.active_instances[instance_id].status = WorkflowStatus.ACTIVE
            return True
        return False
    
    def cancel_workflow(self, instance_id: str) -> bool:
        """Cancel a workflow instance"""
        if instance_id in self.active_instances:
            self.active_instances[instance_id].status = WorkflowStatus.CANCELLED
            return True
        return False

# Predefined workflow templates
def get_production_approval_workflow() -> Dict:
    """Get production approval workflow template"""
    return {
        "id": "production_approval",
        "name": "Production Approval Workflow",
        "description": "Multi-level approval for production orders",
        "version": "1.0",
        "tasks": [
            {
                "id": "create_order",
                "name": "Create Production Order",
                "type": "manual",
                "assignee": "production_manager"
            },
            {
                "id": "quality_review",
                "name": "Quality Review",
                "type": "approval",
                "assignee": "quality_manager"
            },
            {
                "id": "safety_check",
                "name": "Safety Check",
                "type": "approval",
                "assignee": "safety_manager"
            },
            {
                "id": "final_approval",
                "name": "Final Approval",
                "type": "approval",
                "assignee": "plant_manager"
            },
            {
                "id": "start_production",
                "name": "Start Production",
                "type": "automated"
            }
        ],
        "connections": [
            {"from": "create_order", "to": "quality_review"},
            {"from": "quality_review", "to": "safety_check"},
            {"from": "safety_check", "to": "final_approval"},
            {"from": "final_approval", "to": "start_production"}
        ],
        "conditions": {
            "quality_review": "data.quality_score >= 80",
            "safety_check": "data.safety_compliance == true"
        }
    }

def get_quality_control_workflow() -> Dict:
    """Get quality control workflow template"""
    return {
        "id": "quality_control",
        "name": "Quality Control Workflow",
        "description": "Automated quality control process",
        "version": "1.0",
        "tasks": [
            {
                "id": "sample_collection",
                "name": "Collect Sample",
                "type": "manual",
                "assignee": "operator"
            },
            {
                "id": "lab_testing",
                "name": "Lab Testing",
                "type": "automated",
                "assignee": "lab_technician"
            },
            {
                "id": "quality_decision",
                "name": "Quality Decision",
                "type": "decision",
                "assignee": "quality_analyst"
            },
            {
                "id": "approve_batch",
                "name": "Approve Batch",
                "type": "automated"
            },
            {
                "id": "reject_batch",
                "name": "Reject Batch",
                "type": "automated"
            }
        ],
        "connections": [
            {"from": "sample_collection", "to": "lab_testing"},
            {"from": "lab_testing", "to": "quality_decision"},
            {"from": "quality_decision", "to": "approve_batch"},
            {"from": "quality_decision", "to": "reject_batch"}
        ],
        "conditions": {
            "quality_decision": "data.test_results.pass_rate >= 95"
        }
    }
