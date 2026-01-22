/**
 * Service API pour le module Dashboard
 * Endpoints: /api/dashboard/*
 */

import api from './api'
import type {
  Post,
  PostDetail,
  FeedResponse,
  CreatePostData,
  CreateCommentData,
  Comment,
  Like
} from '../types/dashboard'

const BASE_URL = '/api/dashboard'

export const dashboardService = {
  /**
   * Récupère le feed d'actualités (FEED-18: pagination)
   */
  async getFeed(page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get(`${BASE_URL}/feed`, {
      params: { page, page_size: pageSize }
    })
    return response.data
  },

  /**
   * Crée un nouveau post (FEED-01, FEED-03)
   */
  async createPost(data: CreatePostData): Promise<Post> {
    const response = await api.post(`${BASE_URL}/posts`, data)
    return response.data
  },

  /**
   * Récupère les détails d'un post avec médias et commentaires
   */
  async getPost(postId: number): Promise<PostDetail> {
    const response = await api.get(`${BASE_URL}/posts/${postId}`)
    return response.data
  },

  /**
   * Supprime un post (FEED-16: modération)
   */
  async deletePost(postId: number): Promise<void> {
    await api.delete(`${BASE_URL}/posts/${postId}`)
  },

  /**
   * Épingle un post en haut du feed (FEED-08: 48h max)
   */
  async pinPost(postId: number, durationHours = 48): Promise<void> {
    await api.post(`${BASE_URL}/posts/${postId}/pin`, { duration_hours: durationHours })
  },

  /**
   * Désépingle un post
   */
  async unpinPost(postId: number): Promise<void> {
    await api.delete(`${BASE_URL}/posts/${postId}/pin`)
  },

  /**
   * Ajoute un commentaire (FEED-05)
   */
  async addComment(postId: number, data: CreateCommentData): Promise<Comment> {
    const response = await api.post(`${BASE_URL}/posts/${postId}/comments`, data)
    return response.data
  },

  /**
   * Ajoute un like (FEED-04)
   */
  async addLike(postId: number): Promise<Like> {
    const response = await api.post(`${BASE_URL}/posts/${postId}/like`)
    return response.data
  },

  /**
   * Retire un like
   */
  async removeLike(postId: number): Promise<void> {
    await api.delete(`${BASE_URL}/posts/${postId}/like`)
  },
}

export default dashboardService
