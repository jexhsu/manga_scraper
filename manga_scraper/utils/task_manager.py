import subprocess
import uuid
import threading
from datetime import datetime
from sqlalchemy.orm import Session
from manga_scraper.api.models import Task
import psutil


def start_async_scrapy_task(db: Session, cmd: list) -> str:
    """
    Start a scrapy task asynchronously, store task info in PostgreSQL.
    """
    task_id = str(uuid.uuid4())

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Insert new task record
    task = Task(
        task_id=task_id,
        cmd=" ".join(cmd),
        status="running",
        start_time=datetime.utcnow(),
        pid=process.pid,
        is_admin_only=True,
    )
    db.add(task)
    db.commit()

    def watch():
        process.wait()
        # Update status after completion
        finished_time = datetime.utcnow()
        db_task = db.query(Task).filter(Task.task_id == task_id).first()
        if process.returncode == 0:
            db_task.status = "finished"
        else:
            db_task.status = "failed"
        db_task.end_time = finished_time
        db.commit()

    threading.Thread(target=watch, daemon=True).start()

    return task_id


def get_task_status(db: Session, task_id: str) -> dict:
    """
    Retrieve task status and details from the database.
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        return {"task_id": task_id, "status": "not_found"}
    return {
        "task_id": task.task_id,
        "status": task.status,
        "cmd": task.cmd,
        "start_time": task.start_time.isoformat() if task.start_time else None,
        "end_time": task.end_time.isoformat() if task.end_time else None,
        "pid": task.pid,
    }


def list_all_tasks(db: Session) -> list:
    """
    List all tasks stored in the database.
    """
    tasks = db.query(Task).order_by(Task.start_time.desc()).all()
    return [
        {
            "task_id": t.task_id,
            "status": t.status,
            "cmd": t.cmd,
            "start_time": t.start_time.isoformat() if t.start_time else None,
            "end_time": t.end_time.isoformat() if t.end_time else None,
            "pid": t.pid,
        }
        for t in tasks
    ]


def stop_task(db: Session, task_id: str) -> bool:
    """
    Stop a running task by killing its process.
    """

    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task or task.status != "running" or not task.pid:
        return False

    try:
        p = psutil.Process(task.pid)
        p.terminate()  # or p.kill()
        task.status = "terminated"
        task.end_time = datetime.utcnow()
        db.commit()
        return True
    except Exception:
        return False
