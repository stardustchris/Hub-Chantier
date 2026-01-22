import api from './api'
import type { Post, PostCreate, CommentCreate, PaginatedResponse } from '../types'

export interface FeedParams {
  page?: number
  size?: number
}

export const dashboardService = {
  // Feed
  async getFeed(params: FeedParams = {}): Promise<PaginatedResponse<Post>> {
    const response = await api.get<PaginatedResponse<Post>>('/api/dashboard/feed', { params })
    return response.data
  },

  // Posts
  async createPost(data: PostCreate): Promise<Post> {
    const response = await api.post<Post>('/api/dashboard/posts', data)
    return response.data
  },

  async getPost(id: string): Promise<Post> {
    const response = await api.get<Post>(`/api/dashboard/posts/${id}`)
    return response.data
  },

  async deletePost(id: string): Promise<void> {
    await api.delete(`/api/dashboard/posts/${id}`)
  },

  // Pinning
  async pinPost(id: string): Promise<Post> {
    const response = await api.post<Post>(`/api/dashboard/posts/${id}/pin`)
    return response.data
  },

  async unpinPost(id: string): Promise<Post> {
    const response = await api.delete<Post>(`/api/dashboard/posts/${id}/pin`)
    return response.data
  },

  // Comments
  async addComment(postId: string, data: CommentCreate): Promise<Post> {
    const response = await api.post<Post>(`/api/dashboard/posts/${postId}/comments`, data)
    return response.data
  },

  // Likes
  async likePost(postId: string): Promise<Post> {
    const response = await api.post<Post>(`/api/dashboard/posts/${postId}/like`)
    return response.data
  },

  async unlikePost(postId: string): Promise<Post> {
    const response = await api.delete<Post>(`/api/dashboard/posts/${postId}/like`)
    return response.data
  },
}
