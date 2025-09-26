import api from './api';
import { Comment, CreateCommentData } from '../types';

export const commentService = {
  async getComments(projectId: number, issueId: number): Promise<Comment[]> {
    const response = await api.get<Comment[]>(`/projects/${projectId}/issues/${issueId}/comments/`);
    return response.data;
  },

  async createComment(projectId: number, issueId: number, data: CreateCommentData): Promise<Comment> {
    const response = await api.post<Comment>(`/projects/${projectId}/issues/${issueId}/add_comment/`, data);
    return response.data;
  },

  async updateComment(projectId: number, issueId: number, commentId: number, data: CreateCommentData): Promise<Comment> {
    const response = await api.patch<Comment>(`/projects/${projectId}/issues/${issueId}/comments/${commentId}/`, data);
    return response.data;
  },

  async deleteComment(projectId: number, issueId: number, commentId: number): Promise<void> {
    await api.delete(`/projects/${projectId}/issues/${issueId}/comments/${commentId}/`);
  },
};