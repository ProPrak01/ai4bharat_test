import api from './api';
import { ApiResponse, Project, CreateProjectData, ProjectMember } from '../types';

export const projectService = {
  async getProjects(): Promise<ApiResponse<Project>> {
    const response = await api.get<ApiResponse<Project>>('/projects/');
    return response.data;
  },

  async getProject(id: number): Promise<Project> {
    const response = await api.get<Project>(`/projects/${id}/`);
    return response.data;
  },

  async createProject(data: CreateProjectData): Promise<Project> {
    const response = await api.post<Project>('/projects/', data);
    return response.data;
  },

  async updateProject(id: number, data: Partial<CreateProjectData>): Promise<Project> {
    const response = await api.put<Project>(`/projects/${id}/`, data);
    return response.data;
  },

  async deleteProject(id: number): Promise<void> {
    await api.delete(`/projects/${id}/`);
  },

  async getProjectMembers(projectId: number): Promise<ProjectMember[]> {
    const response = await api.get<ProjectMember[]>(`/projects/${projectId}/members/`);
    return response.data;
  },

  async addMember(projectId: number, data: { user_id: number; role: string }): Promise<ProjectMember> {
    const response = await api.post<ProjectMember>(`/projects/${projectId}/add_member/`, data);
    return response.data;
  },

  async removeMember(projectId: number, userId: number): Promise<void> {
    await api.delete(`/projects/${projectId}/members/${userId}/`);
  },

  async updateMemberRole(projectId: number, userId: number, role: string): Promise<ProjectMember> {
    const response = await api.patch<ProjectMember>(`/projects/${projectId}/members/${userId}/`, { role });
    return response.data;
  },
};