import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectService } from '../services/project.service';
import { issueService } from '../services/issue.service';
import type { Project, Issue, CreateIssueData } from '../types';
import Layout from '../components/Layout';
import toast from 'react-hot-toast';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<CreateIssueData>({
    title: '',
    description: '',
    priority: 'medium',
    status: 'open',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchInput, setSearchInput] = useState('');

  useEffect(() => {
    if (id) {
      loadProject();
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      loadIssues();
    }
  }, [id, currentPage, searchQuery]);

  const loadProject = async () => {
    try {
      const projectData = await projectService.getProject(Number(id));
      setProject(projectData);
    } catch (error) {
      console.error('Failed to load project:', error);
      toast.error('Failed to load project');
    } finally {
      setIsLoading(false);
    }
  };

  const loadIssues = async () => {
    try {
      const issuesData = await issueService.getProjectIssues(Number(id), currentPage, searchQuery);
      setIssues(issuesData.results || []);
      setTotalPages(Math.ceil((issuesData.pagination?.count || 0) / 20));
    } catch (error) {
      console.error('Failed to load issues:', error);
      toast.error('Failed to load issues');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await issueService.createIssue(Number(id), formData);
      toast.success('Issue created successfully');
      setShowModal(false);
      setFormData({ title: '', description: '', priority: 'medium', status: 'open' });
      setCurrentPage(1);
      loadIssues();
      loadProject();
    } catch (error) {
      console.error('Failed to create issue:', error);
      toast.error('Failed to create issue');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(searchInput);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getStatusStyle = (status: string) => {
    const styles: Record<string, { bg: string; text: string }> = {
      open: { bg: '#eff6ff', text: '#1e40af' },
      in_progress: { bg: '#fef3c7', text: '#92400e' },
      resolved: { bg: '#dcfce7', text: '#166534' },
      closed: { bg: '#f1f5f9', text: '#475569' }
    };
    return styles[status] || styles.open;
  };

  const getPriorityStyle = (priority: string) => {
    const styles: Record<string, { bg: string; text: string }> = {
      critical: { bg: '#fee2e2', text: '#991b1b' },
      high: { bg: '#fed7aa', text: '#9a3412' },
      medium: { bg: '#fef3c7', text: '#854d0e' },
      low: { bg: '#dbeafe', text: '#1e40af' }
    };
    return styles[priority] || styles.low;
  };

  if (isLoading) {
    return (
      <Layout>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          fontSize: '14px',
          color: '#64748b'
        }}>
          Loading...
        </div>
      </Layout>
    );
  }

  if (!project) {
    return (
      <Layout>
        <div style={{
          textAlign: 'center',
          padding: '64px 20px',
          fontSize: '14px',
          color: '#64748b'
        }}>
          Project not found
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div>
        <div style={{ marginBottom: '24px' }}>
          <Link to="/projects" style={{
            display: 'inline-flex',
            alignItems: 'center',
            fontSize: '14px',
            fontWeight: '500',
            color: '#2563eb',
            textDecoration: 'none'
          }}>
            ← Back to Projects
          </Link>
        </div>

        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '24px',
          marginBottom: '32px'
        }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '600',
            color: '#0f172a',
            marginBottom: '8px'
          }}>
            {project.name}
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#64748b',
            marginBottom: '20px',
            lineHeight: '1.6'
          }}>
            {project.description}
          </p>
          <div style={{
            display: 'flex',
            gap: '20px',
            fontSize: '13px',
            color: '#64748b',
            paddingTop: '16px',
            borderTop: '1px solid #e2e8f0'
          }}>
            <div>
              <span style={{ fontWeight: '500', color: '#0f172a' }}>Owner:</span> {typeof project.owner === 'string' ? project.owner : project.owner.username}
            </div>
            <div>
              <span style={{ fontWeight: '500', color: '#0f172a' }}>{project.member_count}</span> {project.member_count === 1 ? 'member' : 'members'}
            </div>
            <div>
              <span style={{ fontWeight: '500', color: '#0f172a' }}>{project.issue_count}</span> {project.issue_count === 1 ? 'issue' : 'issues'}
            </div>
          </div>
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: '16px',
          marginBottom: '24px',
          flexWrap: 'wrap'
        }}>
          <div style={{ flex: 1, minWidth: '250px' }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#0f172a',
              marginBottom: '4px'
            }}>
              Issues
            </h2>
            <p style={{ fontSize: '14px', color: '#64748b' }}>
              {issues.length > 0 ? `Showing ${issues.length} issues` : 'No issues found'}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search issues..."
                style={{
                  padding: '8px 12px',
                  fontSize: '14px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  backgroundColor: '#ffffff',
                  color: '#0f172a',
                  minWidth: '200px'
                }}
              />
              <button
                type="submit"
                style={{
                  padding: '8px 16px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#64748b',
                  backgroundColor: 'transparent',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Search
              </button>
            </form>

            <button
              onClick={() => setShowModal(true)}
              style={{
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: '500',
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Create Issue
            </button>
          </div>
        </div>

        {issues.length === 0 ? (
          <div style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '64px 32px',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '14px',
              color: '#94a3b8',
              marginBottom: '20px'
            }}>
              {searchQuery ? 'No issues found matching your search' : 'No issues yet. Create your first issue to get started.'}
            </div>
            {!searchQuery && (
              <button
                onClick={() => setShowModal(true)}
                style={{
                  padding: '10px 18px',
                  fontSize: '14px',
                  fontWeight: '500',
                  backgroundColor: '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Create your first issue
              </button>
            )}
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
              {issues.map((issue) => {
                const statusStyle = getStatusStyle(issue.status);
                const priorityStyle = getPriorityStyle(issue.priority);

                return (
                  <Link
                    key={issue.id}
                    to={`/projects/${id}/issues/${issue.id}`}
                    style={{
                      display: 'block',
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      padding: '18px 20px',
                      textDecoration: 'none',
                      color: 'inherit',
                      transition: 'all 0.2s'
                    }}
                  >
                    <h3 style={{
                      fontSize: '16px',
                      fontWeight: '500',
                      color: '#0f172a',
                      marginBottom: '10px'
                    }}>
                      {issue.title}
                    </h3>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                      <span style={{
                        padding: '3px 10px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: statusStyle.bg,
                        color: statusStyle.text,
                        textTransform: 'capitalize'
                      }}>
                        {issue.status.replace('_', ' ')}
                      </span>
                      <span style={{
                        padding: '3px 10px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: priorityStyle.bg,
                        color: priorityStyle.text,
                        textTransform: 'capitalize'
                      }}>
                        {issue.priority}
                      </span>
                      <span style={{
                        fontSize: '13px',
                        color: '#64748b',
                        marginLeft: '4px'
                      }}>
                        {issue.comment_count} {issue.comment_count === 1 ? 'comment' : 'comments'}
                      </span>
                    </div>
                  </Link>
                );
              })}
            </div>

            {totalPages > 1 && (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '8px',
                marginTop: '32px'
              }}>
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  style={{
                    padding: '8px 14px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: currentPage === 1 ? '#94a3b8' : '#0f172a',
                    backgroundColor: 'transparent',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
                  }}
                >
                  Previous
                </button>

                <div style={{ display: 'flex', gap: '4px' }}>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      style={{
                        padding: '8px 12px',
                        fontSize: '14px',
                        fontWeight: '500',
                        color: currentPage === page ? '#ffffff' : '#0f172a',
                        backgroundColor: currentPage === page ? '#2563eb' : 'transparent',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        cursor: 'pointer'
                      }}
                    >
                      {page}
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  style={{
                    padding: '8px 14px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: currentPage === totalPages ? '#94a3b8' : '#0f172a',
                    backgroundColor: 'transparent',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
                  }}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}

        {showModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px'
          }} onClick={() => setShowModal(false)}>
            <div
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                padding: '32px',
                width: '100%',
                maxWidth: '600px',
                maxHeight: '90vh',
                overflowY: 'auto',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <h2 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#0f172a',
                marginBottom: '24px'
              }}>
                Create New Issue
              </h2>

              <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#0f172a',
                    marginBottom: '6px'
                  }}>
                    Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                    placeholder="Enter issue title"
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      fontSize: '14px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      backgroundColor: '#ffffff',
                      color: '#0f172a'
                    }}
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#0f172a',
                    marginBottom: '6px'
                  }}>
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    required
                    rows={4}
                    placeholder="Describe the issue"
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      fontSize: '14px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      backgroundColor: '#ffffff',
                      color: '#0f172a',
                      resize: 'vertical'
                    }}
                  />
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '16px',
                  marginBottom: '24px'
                }}>
                  <div>
                    <label style={{
                      display: 'block',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#0f172a',
                      marginBottom: '6px'
                    }}>
                      Priority
                    </label>
                    <select
                      value={formData.priority}
                      onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        fontSize: '14px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        backgroundColor: '#ffffff',
                        color: '#0f172a'
                      }}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>

                  <div>
                    <label style={{
                      display: 'block',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#0f172a',
                      marginBottom: '6px'
                    }}>
                      Status
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        fontSize: '14px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        backgroundColor: '#ffffff',
                        color: '#0f172a'
                      }}
                    >
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                      <option value="closed">Closed</option>
                    </select>
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  gap: '12px',
                  justifyContent: 'flex-end'
                }}>
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    style={{
                      padding: '10px 18px',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#64748b',
                      backgroundColor: 'transparent',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    style={{
                      padding: '10px 18px',
                      fontSize: '14px',
                      fontWeight: '500',
                      backgroundColor: isSubmitting ? '#94a3b8' : '#2563eb',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: isSubmitting ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {isSubmitting ? 'Creating...' : 'Create Issue'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}