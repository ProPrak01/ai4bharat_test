import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { projectService } from '../services/project.service';
import { issueService } from '../services/issue.service';
import { Project, Issue } from '../types';
import Layout from '../components/Layout';

export default function Dashboard() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [myIssues, setMyIssues] = useState<Issue[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [projectsRes, issuesRes] = await Promise.all([
        projectService.getProjects(),
        issueService.getMyIssues(),
      ]);
      setProjects(projectsRes.results || []);
      setMyIssues(issuesRes.results || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
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

  return (
    <Layout>
      <div>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '600',
            color: '#0f172a',
            marginBottom: '4px'
          }}>
            Welcome back, {user?.username}
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#64748b'
          }}>
            Overview of your projects and issues
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '16px',
          marginBottom: '32px'
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '20px'
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: '500',
              color: '#64748b',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Total Projects
            </div>
            <div style={{
              fontSize: '32px',
              fontWeight: '600',
              color: '#0f172a'
            }}>
              {projects.length}
            </div>
          </div>

          <div style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '20px'
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: '500',
              color: '#64748b',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              My Issues
            </div>
            <div style={{
              fontSize: '32px',
              fontWeight: '600',
              color: '#0f172a'
            }}>
              {myIssues.length}
            </div>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))',
          gap: '24px'
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '24px'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px'
            }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#0f172a'
              }}>
                Recent Projects
              </h2>
              <Link to="/projects" style={{
                fontSize: '14px',
                fontWeight: '500',
                color: '#2563eb',
                textDecoration: 'none'
              }}>
                View all →
              </Link>
            </div>

            {projects.length === 0 ? (
              <div style={{
                padding: '40px 20px',
                textAlign: 'center',
                color: '#94a3b8',
                fontSize: '14px'
              }}>
                No projects yet
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {projects.slice(0, 5).map((project) => (
                  <Link
                    key={project.id}
                    to={`/projects/${project.id}`}
                    style={{
                      display: 'block',
                      padding: '14px 16px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      textDecoration: 'none',
                      color: 'inherit',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{
                      fontSize: '15px',
                      fontWeight: '500',
                      color: '#0f172a',
                      marginBottom: '4px'
                    }}>
                      {project.name}
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: '#64748b'
                    }}>
                      {project.issue_count} {project.issue_count === 1 ? 'issue' : 'issues'}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          <div style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '24px'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#0f172a',
              marginBottom: '20px'
            }}>
              My Recent Issues
            </h2>

            {myIssues.length === 0 ? (
              <div style={{
                padding: '40px 20px',
                textAlign: 'center',
                color: '#94a3b8',
                fontSize: '14px'
              }}>
                No issues assigned to you
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {myIssues.slice(0, 5).map((issue) => {
                  const statusStyle = getStatusStyle(issue.status);
                  const priorityStyle = getPriorityStyle(issue.priority);

                  return (
                    <div
                      key={issue.id}
                      style={{
                        padding: '14px 16px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px'
                      }}
                    >
                      <div style={{
                        fontSize: '15px',
                        fontWeight: '500',
                        color: '#0f172a',
                        marginBottom: '8px'
                      }}>
                        {issue.title}
                      </div>
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
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
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}