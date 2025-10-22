"""Comment service for task discussions (models not implemented, service-only demo)."""

from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from taskflow.models.task import Task
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class CommentService:
    """Service for managing task comments.

    Note: This is a simplified version. In production, you'd have a Comment model.
    This demonstrates service-layer logic without full model implementation.
    """

    def __init__(self, db: Session):
        self.db = db
        # Simulated in-memory storage for demo
        self._comments: Dict[int, List[Dict[str, Any]]] = {}

    def add_comment(
        self,
        task_id: int,
        user_id: int,
        content: str,
    ) -> Dict[str, Any]:
        """Add a comment to a task.

        Args:
            task_id: Task ID
            user_id: User ID who created the comment
            content: Comment content

        Returns:
            Created comment data
        """
        # Verify task exists
        task = self.db.get(Task, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        comment = {
            "id": self._generate_comment_id(task_id),
            "task_id": task_id,
            "user_id": user_id,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None,
        }

        if task_id not in self._comments:
            self._comments[task_id] = []

        self._comments[task_id].append(comment)

        # Update task comment count
        task.comments_count = len(self._comments[task_id])
        self.db.commit()

        logger.info(f"Comment added to task {task_id} by user {user_id}")
        return comment

    def get_task_comments(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all comments for a task."""
        return self._comments.get(task_id, [])

    def updateComment(  # Deliberately camelCase
        self,
        task_id: int,
        comment_id: int,
        content: str,
    ) -> Optional[Dict[str, Any]]:
        """Update a comment."""
        task_comments = self._comments.get(task_id, [])

        for comment in task_comments:
            if comment["id"] == comment_id:
                comment["content"] = content
                comment["updated_at"] = datetime.utcnow().isoformat()
                logger.info(f"Comment {comment_id} updated on task {task_id}")
                return comment

        return None

    def delete_comment(self, task_id: int, comment_id: int) -> bool:
        """Delete a comment."""
        task_comments = self._comments.get(task_id, [])

        for i, comment in enumerate(task_comments):
            if comment["id"] == comment_id:
                del task_comments[i]

                # Update task comment count
                task = self.db.get(Task, task_id)
                if task:
                    task.comments_count = len(task_comments)
                    self.db.commit()

                logger.info(f"Comment {comment_id} deleted from task {task_id}")
                return True

        return False

    def get_recent_comments(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent comments by a user."""
        all_comments = []

        for task_id, comments in self._comments.items():
            for comment in comments:
                if comment["user_id"] == user_id:
                    all_comments.append(comment)

        # Sort by created_at descending
        all_comments.sort(key=lambda c: c["created_at"], reverse=True)

        return all_comments[:limit]

    def count_user_comments(self, user_id: int) -> int:
        """Count total comments by a user."""
        count = 0

        for comments in self._comments.values():
            for comment in comments:
                if comment["user_id"] == user_id:
                    count += 1

        return count

    def search_comments(self, query: str, task_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search comments by content.

        Args:
            query: Search query
            task_id: Optional task filter

        Returns:
            Matching comments
        """
        results = []
        query_lower = query.lower()

        comments_to_search = (
            {task_id: self._comments.get(task_id, [])} if task_id else self._comments
        )

        for tid, comments in comments_to_search.items():
            for comment in comments:
                if query_lower in comment["content"].lower():
                    results.append(comment)

        return results

    def _generate_comment_id(self, task_id: int) -> int:
        """Generate a unique comment ID for a task."""
        task_comments = self._comments.get(task_id, [])
        if not task_comments:
            return 1

        max_id = max(c["id"] for c in task_comments)
        return max_id + 1

    def get_comment_statistics(self) -> Dict[str, Any]:
        """Get overall comment statistics."""
        total_comments = sum(len(comments) for comments in self._comments.values())
        tasks_with_comments = len(self._comments)

        avg_comments_per_task = (
            total_comments / tasks_with_comments if tasks_with_comments > 0 else 0
        )

        return {
            "total_comments": total_comments,
            "tasks_with_comments": tasks_with_comments,
            "avg_comments_per_task": round(avg_comments_per_task, 2),
        }
