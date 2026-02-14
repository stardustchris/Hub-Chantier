/**
 * SignaturePanel - Panneau de signature electronique pour devis
 * Module Devis (Module 20) - DEV-14
 *
 * Fonctionnalites :
 * - 3 modes de signature : dessin tactile (canvas), upload scan, nom/prenom
 * - Affichage de la signature existante avec verification d'integrite
 * - Revocation de signature avec motif
 */

import { useState, useEffect, useRef, useCallback, type ChangeEvent } from 'react'
import { devisService } from '../../services/devis'
import type {
  SignatureDevis,
  SignatureCreate,
  VerificationSignature,
  TypeSignature,
  StatutDevis,
} from '../../types'
import {
  PenTool,
  Upload,
  Type,
  Trash2,
  Check,
  ShieldCheck,
  ShieldX,
  AlertTriangle,
  Loader2,
  X,
  Info,
} from 'lucide-react'

// ===== Props =====
interface SignaturePanelProps {
  devisId: number
  statut: StatutDevis
  onSignatureChange?: () => void
}

// Statuts qui permettent de signer
const STATUTS_SIGNABLES: StatutDevis[] = ['envoye', 'vu', 'en_negociation', 'accepte']

// Taille max upload scan (5 MB)
const MAX_FILE_SIZE = 5 * 1024 * 1024

// ===== Composant principal =====
export default function SignaturePanel({
  devisId,
  statut,
  onSignatureChange,
}: SignaturePanelProps) {
  const [signature, setSignature] = useState<SignatureDevis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isSignable = STATUTS_SIGNABLES.includes(statut)

  const loadSignature = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await devisService.getSignature(devisId)
      setSignature(data)
    } catch {
      setError('Erreur lors du chargement de la signature')
    } finally {
      setLoading(false)
    }
  }, [devisId])

  useEffect(() => {
    loadSignature()
  }, [loadSignature])

  const handleSignatureCreated = useCallback(() => {
    loadSignature()
    onSignatureChange?.()
  }, [loadSignature, onSignatureChange])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
        <AlertTriangle className="flex-shrink-0 mt-0.5 w-4 h-4" />
        <div>
          <p className="text-sm">{error}</p>
          <button onClick={loadSignature} className="text-sm underline mt-1">
            Reessayer
          </button>
        </div>
      </div>
    )
  }

  // Si signe : affichage signature
  if (signature) {
    return (
      <SignatureDisplay
        signature={signature}
        devisId={devisId}
        onRevoked={handleSignatureCreated}
      />
    )
  }

  // Si non signe et statut compatible : formulaire
  if (isSignable) {
    return (
      <SignatureForm
        devisId={devisId}
        onSigned={handleSignatureCreated}
      />
    )
  }

  // Sinon : message informatif
  return (
    <div className="flex items-center gap-3 py-4 text-gray-500">
      <Info className="w-5 h-5 flex-shrink-0" />
      <p className="text-sm">
        La signature est disponible une fois le devis envoye au client.
      </p>
    </div>
  )
}

// ===== SignatureDisplay =====
interface SignatureDisplayProps {
  signature: SignatureDevis
  devisId: number
  onRevoked: () => void
}

function SignatureDisplay({ signature, devisId, onRevoked }: SignatureDisplayProps) {
  const [verification, setVerification] = useState<VerificationSignature | null>(null)
  const [verifying, setVerifying] = useState(false)
  const [showRevokeModal, setShowRevokeModal] = useState(false)
  const [revokeMotif, setRevokeMotif] = useState('')
  const [revoking, setRevoking] = useState(false)

  const isRevoked = !!signature.revoquee_at

  const handleVerify = async () => {
    try {
      setVerifying(true)
      const result = await devisService.verifierSignature(devisId)
      setVerification(result)
    } catch {
      setVerification({
        valide: false,
        hash_actuel: '',
        hash_signature: '',
        integre: false,
        message: 'Erreur lors de la verification',
      })
    } finally {
      setVerifying(false)
    }
  }

  const handleRevoke = async () => {
    if (!revokeMotif.trim()) return
    try {
      setRevoking(true)
      await devisService.revoquerSignature(devisId, revokeMotif.trim())
      setShowRevokeModal(false)
      setRevokeMotif('')
      onRevoked()
    } catch {
      // Erreur geree silencieusement - l'utilisateur verra que rien ne change
    } finally {
      setRevoking(false)
    }
  }

  const truncateHash = (hash: string) =>
    hash.length > 16 ? `${hash.slice(0, 8)}...${hash.slice(-8)}` : hash

  return (
    <div className="space-y-4">
      {/* Badge statut */}
      <div className="flex items-center gap-3">
        {isRevoked ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-700">
            <ShieldX className="w-4 h-4" />
            Signature revoquee
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700">
            <ShieldCheck className="w-4 h-4" />
            Signature valide
          </span>
        )}
      </div>

      {/* Apercu signature */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        {signature.type_signature === 'dessin_tactile' && signature.signature_data.startsWith('data:image') && (
          <img
            src={signature.signature_data}
            alt="Signature dessinee"
            className="max-h-32 mx-auto"
          />
        )}
        {signature.type_signature === 'upload_scan' && signature.signature_data.startsWith('data:image') && (
          <img
            src={signature.signature_data}
            alt="Scan de signature"
            className="max-h-40 mx-auto object-contain"
          />
        )}
        {signature.type_signature === 'nom_prenom' && (
          <p
            className="text-center text-3xl text-gray-800"
            style={{ fontFamily: "'Caveat', 'Dancing Script', cursive" }}
          >
            {signature.signature_data}
          </p>
        )}
      </div>

      {/* Informations */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <div>
          <span className="text-gray-500">Signataire :</span>{' '}
          <span className="font-medium text-gray-900">{signature.signataire_nom}</span>
        </div>
        <div>
          <span className="text-gray-500">Email :</span>{' '}
          <span className="text-gray-900">{signature.signataire_email}</span>
        </div>
        {signature.signataire_telephone && (
          <div>
            <span className="text-gray-500">Telephone :</span>{' '}
            <span className="text-gray-900">{signature.signataire_telephone}</span>
          </div>
        )}
        <div>
          <span className="text-gray-500">Date :</span>{' '}
          <span className="text-gray-900">
            {new Date(signature.horodatage).toLocaleString('fr-FR')}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Type :</span>{' '}
          <span className="text-gray-900">
            {signature.type_signature === 'dessin_tactile'
              ? 'Dessin tactile'
              : signature.type_signature === 'upload_scan'
                ? 'Upload scan'
                : 'Nom et prenom'}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Hash :</span>{' '}
          <code className="text-xs text-gray-600 bg-gray-100 px-1 py-0.5 rounded">
            {truncateHash(signature.hash_document)}
          </code>
        </div>
        {isRevoked && signature.motif_revocation && (
          <div className="sm:col-span-2">
            <span className="text-red-600 font-medium">Motif revocation :</span>{' '}
            <span className="text-gray-900">{signature.motif_revocation}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-2">
        <button
          onClick={handleVerify}
          disabled={verifying}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-sm border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50"
        >
          {verifying ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <ShieldCheck className="w-4 h-4" />
          )}
          Verifier l&apos;integrite
        </button>
        {!isRevoked && (
          <button
            onClick={() => setShowRevokeModal(true)}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-sm border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors"
          >
            <ShieldX className="w-4 h-4" />
            Revoquer
          </button>
        )}
      </div>

      {/* Resultat verification */}
      {verification && (
        <div
          className={`rounded-lg p-3 text-sm ${
            verification.integre
              ? 'bg-green-50 border border-green-200 text-green-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}
          role="status"
        >
          <p className="font-medium">{verification.message}</p>
          <div className="mt-1 text-xs space-y-0.5 opacity-80">
            <p>Hash document actuel : {truncateHash(verification.hash_actuel)}</p>
            <p>Hash au moment de la signature : {truncateHash(verification.hash_signature)}</p>
          </div>
        </div>
      )}

      {/* Modale revocation */}
      {showRevokeModal && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Revoquer la signature"
        >
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Revoquer la signature</h3>
              <button
                onClick={() => setShowRevokeModal(false)}
                className="text-gray-600 hover:text-gray-800"
                aria-label="Fermer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Cette action est irreversible. Veuillez indiquer le motif de revocation.
            </p>
            <textarea
              value={revokeMotif}
              onChange={(e) => setRevokeMotif(e.target.value)}
              placeholder="Motif de la revocation..."
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none"
              autoFocus
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => setShowRevokeModal(false)}
                className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                onClick={handleRevoke}
                disabled={!revokeMotif.trim() || revoking}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {revoking && <Loader2 className="w-4 h-4 animate-spin" />}
                Revoquer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ===== SignatureForm =====
interface SignatureFormProps {
  devisId: number
  onSigned: () => void
}

type TabType = 'dessin' | 'upload' | 'texte'

function SignatureForm({ devisId, onSigned }: SignatureFormProps) {
  const [activeTab, setActiveTab] = useState<TabType>('dessin')
  const [signataireNom, setSignataireNom] = useState('')
  const [signataireEmail, setSignataireEmail] = useState('')
  const [signataireTelephone, setSignataireTelephone] = useState('')
  const [signatureData, setSignatureData] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [showConfirmModal, setShowConfirmModal] = useState(false)

  const typeSignatureMap: Record<TabType, TypeSignature> = {
    dessin: 'dessin_tactile',
    upload: 'upload_scan',
    texte: 'nom_prenom',
  }

  const canSubmit =
    signataireNom.trim() !== '' &&
    signataireEmail.trim() !== '' &&
    signatureData !== ''

  const handleSubmit = async () => {
    if (!canSubmit) return
    try {
      setSubmitting(true)
      setSubmitError(null)
      const payload: SignatureCreate = {
        type_signature: typeSignatureMap[activeTab],
        signataire_nom: signataireNom.trim(),
        signataire_email: signataireEmail.trim(),
        signataire_telephone: signataireTelephone.trim() || undefined,
        signature_data: signatureData,
      }
      await devisService.signerDevis(devisId, payload)
      setShowConfirmModal(false)
      onSigned()
    } catch {
      setSubmitError('Erreur lors de la signature du devis')
    } finally {
      setSubmitting(false)
    }
  }

  // Quand on change d'onglet, reset la donnee de signature
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab)
    setSignatureData('')
  }

  const tabs: { key: TabType; label: string; icon: typeof PenTool }[] = [
    { key: 'dessin', label: 'Dessin tactile', icon: PenTool },
    { key: 'upload', label: 'Upload scan', icon: Upload },
    { key: 'texte', label: 'Signature textuelle', icon: Type },
  ]

  return (
    <div className="space-y-4">
      {/* Onglets */}
      <div className="flex border-b border-gray-200" role="tablist">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            role="tab"
            aria-selected={activeTab === key}
            onClick={() => handleTabChange(key)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Icon className="w-4 h-4" />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>

      {/* Zone de signature selon l'onglet */}
      <div role="tabpanel" className="min-h-[200px]">
        {activeTab === 'dessin' && (
          <CanvasSignature
            onDataChange={setSignatureData}
          />
        )}
        {activeTab === 'upload' && (
          <UploadSignature
            onDataChange={setSignatureData}
          />
        )}
        {activeTab === 'texte' && (
          <TextSignature
            onDataChange={setSignatureData}
          />
        )}
      </div>

      {/* Champs communs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label htmlFor="sig-nom" className="block text-sm font-medium text-gray-700 mb-1">
            Nom du signataire <span className="text-red-500">*</span>
          </label>
          <input
            id="sig-nom"
            type="text"
            value={signataireNom}
            onChange={(e) => setSignataireNom(e.target.value)}
            placeholder="Jean Dupont"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        <div>
          <label htmlFor="sig-email" className="block text-sm font-medium text-gray-700 mb-1">
            Email du signataire <span className="text-red-500">*</span>
          </label>
          <input
            id="sig-email"
            type="email"
            value={signataireEmail}
            onChange={(e) => setSignataireEmail(e.target.value)}
            placeholder="jean.dupont@email.com"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        <div>
          <label htmlFor="sig-tel" className="block text-sm font-medium text-gray-700 mb-1">
            Telephone (optionnel)
          </label>
          <input
            id="sig-tel"
            type="tel"
            value={signataireTelephone}
            onChange={(e) => setSignataireTelephone(e.target.value)}
            placeholder="06 12 34 56 78"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Erreur */}
      {submitError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm flex items-center gap-2" role="alert">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          {submitError}
        </div>
      )}

      {/* Bouton signer */}
      <div className="pt-2">
        <button
          onClick={() => setShowConfirmModal(true)}
          disabled={!canSubmit}
          className="inline-flex items-center gap-2 px-6 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <PenTool className="w-4 h-4" />
          Signer le devis
        </button>
      </div>

      {/* Modale de confirmation */}
      {showConfirmModal && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Confirmer la signature"
        >
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Confirmer la signature</h3>
              <button
                onClick={() => setShowConfirmModal(false)}
                className="text-gray-600 hover:text-gray-800"
                aria-label="Fermer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              Vous etes sur le point de signer ce devis en tant que :
            </p>
            <p className="text-sm font-medium text-gray-900 mb-1">{signataireNom}</p>
            <p className="text-sm text-gray-600 mb-4">{signataireEmail}</p>
            <p className="text-xs text-gray-500 mb-4">
              En signant, vous confirmez avoir pris connaissance du contenu du devis et acceptez ses termes.
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Check className="w-4 h-4" />
                )}
                Confirmer et signer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ===== CanvasSignature (dessin tactile) =====
interface CanvasSignatureProps {
  onDataChange: (data: string) => void
}

function CanvasSignature({ onDataChange }: CanvasSignatureProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const isDrawingRef = useRef(false)
  const lastPosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 })
  const hasContentRef = useRef(false)

  const getCanvasPos = useCallback(
    (e: MouseEvent | TouchEvent): { x: number; y: number } => {
      const canvas = canvasRef.current
      if (!canvas) return { x: 0, y: 0 }
      const rect = canvas.getBoundingClientRect()
      const scaleX = canvas.width / rect.width
      const scaleY = canvas.height / rect.height

      if ('touches' in e) {
        const touch = e.touches[0]
        return {
          x: (touch.clientX - rect.left) * scaleX,
          y: (touch.clientY - rect.top) * scaleY,
        }
      }
      return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY,
      }
    },
    []
  )

  const startDraw = useCallback(
    (e: MouseEvent | TouchEvent) => {
      isDrawingRef.current = true
      lastPosRef.current = getCanvasPos(e)
    },
    [getCanvasPos]
  )

  const draw = useCallback(
    (e: MouseEvent | TouchEvent) => {
      if (!isDrawingRef.current) return
      e.preventDefault()
      const canvas = canvasRef.current
      const ctx = canvas?.getContext('2d')
      if (!ctx || !canvas) return

      const pos = getCanvasPos(e)
      ctx.beginPath()
      ctx.moveTo(lastPosRef.current.x, lastPosRef.current.y)
      ctx.lineTo(pos.x, pos.y)
      ctx.strokeStyle = '#1a1a1a'
      ctx.lineWidth = 2.5
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.stroke()
      lastPosRef.current = pos
      hasContentRef.current = true
    },
    [getCanvasPos]
  )

  const endDraw = useCallback(() => {
    if (isDrawingRef.current && hasContentRef.current) {
      isDrawingRef.current = false
      const canvas = canvasRef.current
      if (canvas) {
        onDataChange(canvas.toDataURL('image/png'))
      }
    }
    isDrawingRef.current = false
  }, [onDataChange])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    // Initialiser le canvas
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
    }

    // Mouse events
    const handleMouseDown = (e: MouseEvent) => startDraw(e)
    const handleMouseMove = (e: MouseEvent) => draw(e)
    const handleMouseUp = () => endDraw()
    const handleMouseLeave = () => endDraw()

    // Touch events
    const handleTouchStart = (e: TouchEvent) => {
      e.preventDefault()
      startDraw(e)
    }
    const handleTouchMove = (e: TouchEvent) => draw(e)
    const handleTouchEnd = () => endDraw()

    canvas.addEventListener('mousedown', handleMouseDown)
    canvas.addEventListener('mousemove', handleMouseMove)
    canvas.addEventListener('mouseup', handleMouseUp)
    canvas.addEventListener('mouseleave', handleMouseLeave)
    canvas.addEventListener('touchstart', handleTouchStart, { passive: false })
    canvas.addEventListener('touchmove', handleTouchMove, { passive: false })
    canvas.addEventListener('touchend', handleTouchEnd)

    return () => {
      canvas.removeEventListener('mousedown', handleMouseDown)
      canvas.removeEventListener('mousemove', handleMouseMove)
      canvas.removeEventListener('mouseup', handleMouseUp)
      canvas.removeEventListener('mouseleave', handleMouseLeave)
      canvas.removeEventListener('touchstart', handleTouchStart)
      canvas.removeEventListener('touchmove', handleTouchMove)
      canvas.removeEventListener('touchend', handleTouchEnd)
    }
  }, [startDraw, draw, endDraw])

  const handleClear = () => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (ctx && canvas) {
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      hasContentRef.current = false
      onDataChange('')
    }
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-gray-600">
        Dessinez votre signature dans le cadre ci-dessous (souris ou ecran tactile).
      </p>
      <div className="relative border-2 border-dashed border-gray-300 rounded-lg overflow-hidden bg-white">
        <canvas
          ref={canvasRef}
          width={600}
          height={200}
          className="w-full cursor-crosshair touch-none"
          style={{ maxHeight: '200px' }}
          aria-label="Zone de dessin de signature"
        />
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={handleClear}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Effacer
        </button>
      </div>
    </div>
  )
}

// ===== UploadSignature =====
interface UploadSignatureProps {
  onDataChange: (data: string) => void
}

function UploadSignature({ onDataChange }: UploadSignatureProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    setFileError(null)

    if (!file) {
      setPreview(null)
      onDataChange('')
      return
    }

    // Verifier le type
    if (!file.type.startsWith('image/')) {
      setFileError('Veuillez selectionner une image (JPG, PNG).')
      setPreview(null)
      onDataChange('')
      return
    }

    // Verifier la taille
    if (file.size > MAX_FILE_SIZE) {
      setFileError('Le fichier est trop volumineux (max 5 Mo).')
      setPreview(null)
      onDataChange('')
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result as string
      setPreview(result)
      onDataChange(result)
    }
    reader.readAsDataURL(file)
  }

  const handleRemove = () => {
    setPreview(null)
    onDataChange('')
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-600">
        Importez un scan ou une photo de votre signature (JPG ou PNG, 5 Mo max).
      </p>

      {!preview ? (
        <label
          htmlFor="sig-upload"
          className="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
        >
          <Upload className="w-8 h-8 text-gray-600 mb-2" />
          <span className="text-sm text-gray-500">Cliquez ou glissez une image</span>
          <span className="text-xs text-gray-600 mt-1">JPG, PNG - 5 Mo max</span>
          <input
            ref={inputRef}
            id="sig-upload"
            type="file"
            accept="image/jpeg,image/png"
            onChange={handleFileChange}
            className="sr-only"
          />
        </label>
      ) : (
        <div className="relative border border-gray-200 rounded-lg p-3 bg-gray-50">
          <img
            src={preview}
            alt="Apercu du scan de signature"
            className="max-h-40 mx-auto object-contain"
          />
          <button
            type="button"
            onClick={handleRemove}
            className="absolute top-2 right-2 p-1 bg-white border border-gray-300 rounded-full text-gray-500 hover:text-red-600 hover:border-red-300 transition-colors"
            aria-label="Supprimer l'image"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {fileError && (
        <p className="text-sm text-red-600 flex items-center gap-1.5">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          {fileError}
        </p>
      )}
    </div>
  )
}

// ===== TextSignature =====
interface TextSignatureProps {
  onDataChange: (data: string) => void
}

function TextSignature({ onDataChange }: TextSignatureProps) {
  const [text, setText] = useState('')

  const handleChange = (value: string) => {
    setText(value)
    onDataChange(value.trim())
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-600">
        Saisissez votre nom et prenom. La signature sera affichee en style manuscrit.
      </p>
      <input
        type="text"
        value={text}
        onChange={(e) => handleChange(e.target.value)}
        placeholder="Prenom Nom"
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        aria-label="Signature textuelle"
      />
      {text.trim() && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
          <p className="text-xs text-gray-600 mb-2">Apercu :</p>
          <p
            className="text-3xl text-gray-800"
            style={{ fontFamily: "'Caveat', 'Dancing Script', cursive" }}
          >
            {text}
          </p>
        </div>
      )}
    </div>
  )
}
