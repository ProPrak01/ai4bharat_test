export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  date_joined: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  owner: string | User;
  member_count: number;
  issue_count: number;
  created_at: string;
  updated_at: string;
  members?: ProjectMember[];
}

export interface ProjectMember {
  id: number;
  user: User;
  role: 'member' | 'admin';
  joined_at: string;
}

export type IssueStatus = 'open' | 'in_progress' | 'resolved' | 'closed';
export type IssuePriority = 'low' | 'medium' | 'high' | 'critical';

export interface Issue {
  id: number;
  title: string;
  description: string;
  status: IssueStatus;
  priority: IssuePriority;
  project?: Project;
  project_name?: string;
  reporter: string | User;
  assignee: (string | User) | null;
  comment_count: number;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  content: string;
  author: string | User;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  pagination?: {
    count: number;
    next: string | null;
    previous: string | null;
    page_size: number;
    total_pages: number;
    current_page: number;
  };
  results?: T[];
  data?: T;
}

export interface ApiError {
  error: boolean;
  message: string;
  details?: Record<string, string[]>;
  status_code: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

export interface AuthResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
  message: string;
}

export interface CreateProjectData {
  name: string;
  description: string;
}

export interface CreateIssueData {
  title: string;
  description: string;
  priority: IssuePriority;
  status: IssueStatus;
  assignee_id?: number | null;
}

export interface UpdateIssueData {
  title?: string;
  description?: string;
  priority?: IssuePriority;
  status?: IssueStatus;
  assignee_id?: number | null;
}

export interface CreateCommentData {
  content: string;
}