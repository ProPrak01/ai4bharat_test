import api from './api';
import { ApiResponse, Issue, CreateIssueData, UpdateIssueData } from '../types';

export const issueService = {
  async getProjectIssues(projectId: number, page: number = 1, search: string = ''): Promise<ApiResponse<Issue>> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    if (search) {
      params.append('search', search);
    }
    const response = await api.get<ApiResponse<Issue>>(`/projects/${projectId}/issues/?${params.toString()}`);
    return response.data;
  },

  async getIssue(projectId: number, issueId: number): Promise<Issue> {
    const response = await api.get<Issue>(`/projects/${projectId}/issues/${issueId}/`);
    return response.data;
  },

  async createIssue(projectId: number, data: CreateIssueData): Promise<Issue> {
    const response = await api.post<Issue>(`/projects/${projectId}/issues/`, data);
    return response.data;
  },

  async updateIssue(projectId: number, issueId: number, data: UpdateIssueData): Promise<Issue> {
    const response = await api.patch<Issue>(`/projects/${projectId}/issues/${issueId}/`, data);
    return response.data;
  },

  async deleteIssue(projectId: number, issueId: number): Promise<void> {
    await api.delete(`/projects/${projectId}/issues/${issueId}/`);
  },

  async getAllIssues(): Promise<ApiResponse<Issue>> {
    const response = await api.get<ApiResponse<Issue>>('/issues/');
    return response.data;
  },

  async getMyIssues(): Promise<ApiResponse<Issue>> {
    const response = await api.get<ApiResponse<Issue>>('/my-issues/');
    return response.data;
  },
};