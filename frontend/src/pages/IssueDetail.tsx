import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { issueService } from '../services/issue.service';
import { commentService } from '../services/comment.service';
import type { Issue, Comment } from '../types';
import Layout from '../components/Layout';
import toast from 'react-hot-toast';

export default function IssueDetail() {
  const { projectId, issueId } = useParams<{ projectId: string; issueId: string }>();
  const [issue, setIssue] = useState<Issue | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (projectId && issueId) {
      loadData();
    }
  }, [projectId, issueId]);

  const loadData = async () => {
    try {
      const [issueData, commentsData] = await Promise.all([
        issueService.getIssue(Number(projectId), Number(issueId)),
        commentService.getComments(Number(projectId), Number(issueId)),
      ]);
      setIssue(issueData);
      setComments(commentsData);
    } catch (error) {
      console.error('Failed to load issue:', error);
      toast.error('Failed to load issue');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setIsSubmitting(true);
    try {
      await commentService.createComment(Number(projectId), Number(issueId), { content: newComment });
      toast.success('Comment added');
      setNewComment('');
      loadData();
    } catch (error) {
      console.error('Failed to add comment:', error);
      toast.error('Failed to add comment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    try {
      await issueService.updateIssue(Number(projectId), Number(issueId), { status: newStatus as any });
      toast.success('Status updated');
      loadData();
    } catch (error) {
      console.error('Failed to update status:', error);
      toast.error('Failed to update status');
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div>Loading...</div>
      </Layout>
    );
  }

  if (!issue) {
    return (
      <Layout>
        <div>Issue not found</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div>
        <div style={{ marginBottom: '24px' }}>
          <Link to={`/projects/${projectId}`} style={{ color: '#3b82f6', textDecoration: 'none', fontSize: '14px' }}>
            ← Back to Project
          </Link>
        </div>

        <div style={{ background: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: 'bold', flex: 1 }}>{issue.title}</h1>
            <select
              value={issue.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '14px' }}
            >
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
            <span style={{
              padding: '4px 12px',
              borderRadius: '4px',
              fontSize: '14px',
              fontWeight: '500',
              background: issue.status === 'open' ? '#dbeafe' : issue.status === 'in_progress' ? '#fef3c7' : issue.status === 'resolved' ? '#d1fae5' : '#e5e7eb',
              color: issue.status === 'open' ? '#1e40af' : issue.status === 'in_progress' ? '#92400e' : issue.status === 'resolved' ? '#065f46' : '#374151'
            }}>
              {issue.status}
            </span>
            <span style={{
              padding: '4px 12px',
              borderRadius: '4px',
              fontSize: '14px',
              fontWeight: '500',
              background: issue.priority === 'critical' ? '#fee2e2' : issue.priority === 'high' ? '#fed7aa' : issue.priority === 'medium' ? '#fef3c7' : '#e5e7eb',
              color: issue.priority === 'critical' ? '#991b1b' : issue.priority === 'high' ? '#9a3412' : issue.priority === 'medium' ? '#92400e' : '#374151'
            }}>
              {issue.priority}
            </span>
          </div>

          <p style={{ color: '#374151', marginBottom: '16px', whiteSpace: 'pre-wrap' }}>{issue.description}</p>

          <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#6b7280', paddingTop: '16px', borderTop: '1px solid #e5e7eb' }}>
            <span>Reporter: {typeof issue.reporter === 'string' ? issue.reporter : issue.reporter.username}</span>
            <span>Assignee: {issue.assignee ? (typeof issue.assignee === 'string' ? issue.assignee : issue.assignee.username) : 'Unassigned'}</span>
            <span>Created: {new Date(issue.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        <div style={{ background: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>
            Comments ({comments.length})
          </h2>

          <form onSubmit={handleSubmitComment} style={{ marginBottom: '24px' }}>
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              rows={3}
              style={{ width: '100%', padding: '12px', border: '1px solid #d1d5db', borderRadius: '4px', marginBottom: '12px' }}
            />
            <button
              type="submit"
              disabled={isSubmitting || !newComment.trim()}
              style={{
                padding: '10px 20px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontWeight: '500',
                cursor: 'pointer',
                opacity: (isSubmitting || !newComment.trim()) ? 0.5 : 1
              }}
            >
              {isSubmitting ? 'Posting...' : 'Post Comment'}
            </button>
          </form>

          {comments.length === 0 ? (
            <p style={{ color: '#6b7280', textAlign: 'center', padding: '24px' }}>No comments yet</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {comments.map((comment) => (
                <div key={comment.id} style={{ padding: '16px', background: '#f9fafb', borderRadius: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: '600', fontSize: '14px' }}>
                      {typeof comment.author === 'string' ? comment.author : comment.author.username}
                    </span>
                    <span style={{ fontSize: '12px', color: '#6b7280' }}>
                      {new Date(comment.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p style={{ color: '#374151', whiteSpace: 'pre-wrap' }}>{comment.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}