import api from './api'
import type {
  Article,
  ArticleCreate,
  ArticleUpdate,
  Devis,
  DevisCreate,
  DevisUpdate,
  DevisDetail,
  LotDevis,
  LotDevisCreate,
  LotDevisUpdate,
  LigneDevis,
  LigneDevisCreate,
  LigneDevisUpdate,
  JournalDevisEntry,
  DashboardDevis,
  VersionDevis,
  ComparatifDevis,
  LabelVariante,
  EligibiliteTVA,
  AttestationTVA,
  AttestationTVACreate,
  FraisChantierDevis,
  FraisChantierCreate,
  FraisChantierUpdate,
  RepartitionFraisLot,
  OptionsPresentation,
  TemplatePresentation,
  SignatureDevis,
  SignatureCreate,
  VerificationSignature,
  ConversionInfo,
  RelancesHistorique,
  ConfigRelances,
  ConvertirDevisResult,
  PieceJointeDevis,
} from '../types'

/**
 * Helper: le backend Phase 2 peut renvoyer soit un tableau direct,
 * soit un objet wrappé { items: [...] } ou { key: [...] }.
 * Cette fonction extrait toujours un tableau.
 */
function extractArray<T>(data: unknown, key?: string): T[] {
  if (Array.isArray(data)) return data as T[]
  if (data && typeof data === 'object') {
    const obj = data as Record<string, unknown>
    if (key && Array.isArray(obj[key])) return obj[key] as T[]
    if (Array.isArray(obj.items)) return obj.items as T[]
    // Cherche le premier champ qui est un tableau
    for (const v of Object.values(obj)) {
      if (Array.isArray(v)) return v as T[]
    }
  }
  return []
}

// Backend router: APIRouter(prefix="/devis") -> mounted at /api/devis
const BASE = '/api/devis'
// Articles have a separate router: APIRouter(prefix="/articles-devis")
const ARTICLES_BASE = '/api/articles-devis'

export const devisService = {
  // ===== Articles (DEV-01) =====
  async listArticles(params?: {
    categorie?: string
    search?: string
    actif?: boolean
    limit?: number
    offset?: number
  }): Promise<{ items: Article[]; total: number }> {
    const response = await api.get<{ items: Article[]; total: number }>(
      ARTICLES_BASE,
      { params }
    )
    return response.data
  },

  async getArticle(id: number): Promise<Article> {
    const response = await api.get<Article>(`${ARTICLES_BASE}/${id}`)
    return response.data
  },

  async createArticle(data: ArticleCreate): Promise<Article> {
    const response = await api.post<Article>(ARTICLES_BASE, data)
    return response.data
  },

  async updateArticle(id: number, data: ArticleUpdate): Promise<Article> {
    const response = await api.put<Article>(`${ARTICLES_BASE}/${id}`, data)
    return response.data
  },

  async deleteArticle(id: number): Promise<void> {
    await api.delete(`${ARTICLES_BASE}/${id}`)
  },

  // ===== Devis (DEV-03) =====
  async listDevis(params?: {
    statut?: string
    client_nom?: string
    date_min?: string
    date_max?: string
    montant_min?: number
    montant_max?: number
    search?: string
    commercial_id?: number
    limit?: number
    offset?: number
  }): Promise<{ items: Devis[]; total: number }> {
    const response = await api.get<{ items: Devis[]; total: number }>(
      BASE,
      { params }
    )
    return response.data
  },

  async getDevis(id: number): Promise<DevisDetail> {
    const response = await api.get<DevisDetail>(`${BASE}/${id}`)
    return response.data
  },

  async createDevis(data: DevisCreate): Promise<Devis> {
    const response = await api.post<Devis>(BASE, data)
    return response.data
  },

  async updateDevis(id: number, data: DevisUpdate): Promise<Devis> {
    const response = await api.put<Devis>(`${BASE}/${id}`, data)
    return response.data
  },

  async deleteDevis(id: number): Promise<void> {
    await api.delete(`${BASE}/${id}`)
  },

  // ===== Workflow (DEV-15) =====
  async soumettreDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/soumettre`)
    return response.data
  },

  async validerDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/valider`)
    return response.data
  },

  async retournerBrouillon(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/retourner-brouillon`)
    return response.data
  },

  async accepterDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/accepter`)
    return response.data
  },

  async refuserDevis(id: number, motif: string): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/refuser`, { motif })
    return response.data
  },

  async marquerPerdu(id: number, motif: string): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/perdu`, { motif })
    return response.data
  },

  // ===== Calcul totaux (DEV-06) =====
  async calculerTotaux(id: number): Promise<Record<string, unknown>> {
    const response = await api.post<Record<string, unknown>>(`${BASE}/${id}/calculer`)
    return response.data
  },

  // ===== Lots (DEV-03) =====
  async createLot(data: LotDevisCreate): Promise<LotDevis> {
    const { devis_id } = data
    const response = await api.post<LotDevis>(`${BASE}/${devis_id}/lots`, data)
    return response.data
  },

  async updateLot(id: number, data: LotDevisUpdate): Promise<LotDevis> {
    const response = await api.put<LotDevis>(`${BASE}/lots/${id}`, data)
    return response.data
  },

  async deleteLot(id: number): Promise<void> {
    await api.delete(`${BASE}/lots/${id}`)
  },

  // ===== Lignes (DEV-03) =====
  async createLigne(data: LigneDevisCreate): Promise<LigneDevis> {
    const { lot_devis_id } = data
    const response = await api.post<LigneDevis>(`${BASE}/lots/${lot_devis_id}/lignes`, data)
    return response.data
  },

  async updateLigne(id: number, data: LigneDevisUpdate): Promise<LigneDevis> {
    const response = await api.put<LigneDevis>(`${BASE}/lignes/${id}`, data)
    return response.data
  },

  async deleteLigne(id: number): Promise<void> {
    await api.delete(`${BASE}/lignes/${id}`)
  },

  // ===== Dashboard (DEV-17) =====
  async getDashboard(): Promise<DashboardDevis> {
    const response = await api.get(`${BASE}/dashboard`)
    const raw = response.data
    // Le backend renvoie certains champs numériques en string (Decimal serialisé)
    return {
      kpi: {
        ...raw.kpi,
        total_pipeline_ht: Number(raw.kpi.total_pipeline_ht) || 0,
        total_accepte_ht: Number(raw.kpi.total_accepte_ht) || 0,
        taux_conversion: Number(raw.kpi.taux_conversion) || 0,
      },
      derniers_devis: (raw.derniers_devis || []).map((d: Record<string, unknown>) => ({
        ...d,
        montant_total_ht: Number(d.montant_total_ht) || 0,
      })),
    } as DashboardDevis
  },

  // ===== Journal (DEV-18) =====
  async listJournal(devisId: number, params?: {
    limit?: number
    offset?: number
  }): Promise<{ items: JournalDevisEntry[]; total: number }> {
    const response = await api.get<{ items: JournalDevisEntry[]; total: number }>(
      `${BASE}/${devisId}/journal`,
      { params }
    )
    return response.data
  },

  // ===== Search (DEV-19) =====
  async searchDevis(params?: {
    client_nom?: string
    statut?: string
    date_min?: string
    date_max?: string
    montant_min?: number
    montant_max?: number
    commercial_id?: number
    search?: string
    limit?: number
    offset?: number
  }): Promise<{ items: Devis[]; total: number }> {
    const response = await api.get<{ items: Devis[]; total: number }>(
      `${BASE}/search`,
      { params }
    )
    return response.data
  },

  // ===== Versions et variantes (DEV-08) =====
  async creerRevision(devisId: number, commentaire?: string): Promise<Devis> {
    const response = await api.post<Devis>(
      `${BASE}/${devisId}/revisions`,
      commentaire ? { commentaire } : {}
    )
    return response.data
  },

  async creerVariante(devisId: number, labelVariante: LabelVariante, commentaire?: string): Promise<Devis> {
    const body: { label_variante: LabelVariante; commentaire?: string } = {
      label_variante: labelVariante,
    }
    if (commentaire) {
      body.commentaire = commentaire
    }
    const response = await api.post<Devis>(`${BASE}/${devisId}/variantes`, body)
    return response.data
  },

  async listerVersions(devisId: number): Promise<VersionDevis[]> {
    const response = await api.get(`${BASE}/${devisId}/versions`)
    return extractArray<VersionDevis>(response.data, 'versions')
  },

  async genererComparatif(sourceId: number, cibleId: number): Promise<ComparatifDevis> {
    const response = await api.post<ComparatifDevis>(
      `${BASE}/${sourceId}/comparer/${cibleId}`
    )
    return response.data
  },

  async getComparatif(comparatifId: number): Promise<ComparatifDevis> {
    const response = await api.get<ComparatifDevis>(
      `${BASE}/comparatifs/${comparatifId}`
    )
    return response.data
  },

  async figerVersion(devisId: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${devisId}/figer`)
    return response.data
  },

  // ===== Attestation TVA (DEV-23) =====
  async verifierEligibiliteTVA(devisId: number): Promise<EligibiliteTVA> {
    const response = await api.get<EligibiliteTVA>(`${BASE}/${devisId}/eligibilite-tva`)
    return response.data
  },

  async genererAttestationTVA(devisId: number, data: AttestationTVACreate): Promise<AttestationTVA> {
    const response = await api.post<AttestationTVA>(`${BASE}/${devisId}/attestation-tva`, data)
    return response.data
  },

  async getAttestationTVA(devisId: number): Promise<AttestationTVA> {
    const response = await api.get<AttestationTVA>(`${BASE}/${devisId}/attestation-tva`)
    return response.data
  },

  // ===== Frais de chantier (DEV-25) =====
  async listFraisChantier(devisId: number): Promise<FraisChantierDevis[]> {
    const response = await api.get(`${BASE}/${devisId}/frais-chantier`)
    return extractArray<FraisChantierDevis>(response.data)
  },

  async createFraisChantier(devisId: number, data: FraisChantierCreate): Promise<FraisChantierDevis> {
    const response = await api.post<FraisChantierDevis>(`${BASE}/${devisId}/frais-chantier`, data)
    return response.data
  },

  async updateFraisChantier(fraisId: number, data: FraisChantierUpdate): Promise<FraisChantierDevis> {
    const response = await api.put<FraisChantierDevis>(`${BASE}/frais-chantier/${fraisId}`, data)
    return response.data
  },

  async deleteFraisChantier(fraisId: number): Promise<void> {
    await api.delete(`${BASE}/frais-chantier/${fraisId}`)
  },

  async getRepartitionFrais(devisId: number): Promise<RepartitionFraisLot[]> {
    const response = await api.get(`${BASE}/${devisId}/frais-chantier/repartition`)
    return extractArray<RepartitionFraisLot>(response.data)
  },

  // ===== Options de presentation (DEV-11) =====
  async getTemplatesPresentation(): Promise<TemplatePresentation[]> {
    const response = await api.get(`${BASE}/templates-presentation`)
    return extractArray<TemplatePresentation>(response.data, 'templates')
  },

  async getOptionsPresentation(devisId: number): Promise<OptionsPresentation> {
    const response = await api.get<OptionsPresentation>(`${BASE}/${devisId}/options-presentation`)
    return response.data
  },

  async updateOptionsPresentation(
    devisId: number,
    data: { template_nom?: string } & Partial<OptionsPresentation>
  ): Promise<OptionsPresentation> {
    const response = await api.put<OptionsPresentation>(`${BASE}/${devisId}/options-presentation`, data)
    return response.data
  },

  // ===== Signature electronique (DEV-14) =====
  async signerDevis(devisId: number, data: SignatureCreate): Promise<SignatureDevis> {
    const response = await api.post<SignatureDevis>(`${BASE}/${devisId}/signature`, data)
    return response.data
  },

  async getSignature(devisId: number): Promise<SignatureDevis | null> {
    try {
      const response = await api.get<SignatureDevis>(`${BASE}/${devisId}/signature`)
      return response.data
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number } }
      if (axiosErr.response?.status === 404) {
        return null
      }
      throw err
    }
  },

  async revoquerSignature(devisId: number, motif: string): Promise<void> {
    await api.post(`${BASE}/${devisId}/signature/revoquer`, { motif })
  },

  async verifierSignature(devisId: number): Promise<VerificationSignature> {
    const response = await api.get<VerificationSignature>(`${BASE}/${devisId}/signature/verifier`)
    return response.data
  },

  // ===== Conversion en chantier (DEV-16) =====
  async getConversionInfo(devisId: number): Promise<ConversionInfo> {
    const response = await api.get<ConversionInfo>(`${BASE}/${devisId}/conversion-info`)
    return response.data
  },

  async convertirEnChantier(
    devisId: number,
    options?: { notify_client?: boolean; notify_team?: boolean }
  ): Promise<ConvertirDevisResult> {
    const response = await api.post<{
      success: boolean
      message: string
      data: ConvertirDevisResult
    }>(`${BASE}/${devisId}/convertir-en-chantier`, {
      notify_client: options?.notify_client ?? false,
      notify_team: options?.notify_team ?? true,
    })
    return response.data.data
  },

  // ===== Relances automatiques (DEV-24) =====
  async getRelances(devisId: number): Promise<RelancesHistorique> {
    const response = await api.get<RelancesHistorique>(`${BASE}/${devisId}/relances`)
    return response.data
  },

  async planifierRelances(devisId: number, config?: Partial<ConfigRelances>): Promise<{ relances_planifiees: RelancesHistorique['relances']; nb_planifiees: number }> {
    const response = await api.post<{ relances_planifiees: RelancesHistorique['relances']; nb_planifiees: number }>(
      `${BASE}/${devisId}/relances/planifier`,
      config ?? {}
    )
    return response.data
  },

  async annulerRelances(devisId: number): Promise<{ nb_annulees: number }> {
    const response = await api.post<{ nb_annulees: number }>(`${BASE}/${devisId}/relances/annuler`)
    return response.data
  },

  async getConfigRelances(devisId: number): Promise<ConfigRelances> {
    const response = await api.get<ConfigRelances>(`${BASE}/${devisId}/config-relances`)
    return response.data
  },

  async updateConfigRelances(devisId: number, config: Partial<ConfigRelances>): Promise<ConfigRelances> {
    const response = await api.put<ConfigRelances>(`${BASE}/${devisId}/config-relances`, config)
    return response.data
  },

  // ===== Pieces jointes (DEV-07) =====
  async listPiecesJointes(devisId: number): Promise<PieceJointeDevis[]> {
    const response = await api.get(`${BASE}/${devisId}/pieces-jointes`)
    return extractArray<PieceJointeDevis>(response.data)
  },

  async uploadPieceJointe(devisId: number, data: {
    nom_fichier: string
    type_fichier: string
    taille_octets: number
    mime_type: string
    visible_client?: boolean
    document_id?: number
  }): Promise<PieceJointeDevis> {
    const response = await api.post<PieceJointeDevis>(`${BASE}/${devisId}/pieces-jointes`, data)
    return response.data
  },

  async deletePieceJointe(pieceId: number): Promise<void> {
    await api.delete(`${BASE}/pieces-jointes/${pieceId}`)
  },

  async toggleVisibilitePieceJointe(pieceId: number, visible: boolean): Promise<PieceJointeDevis> {
    const response = await api.patch<PieceJointeDevis>(
      `${BASE}/pieces-jointes/${pieceId}/visibilite`,
      { visible_client: visible }
    )
    return response.data
  },
}
