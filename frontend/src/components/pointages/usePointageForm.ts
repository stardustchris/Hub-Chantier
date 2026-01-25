/**
 * Hook usePointageForm - Gestion de l'état et des actions du formulaire de pointage
 * Extrait de PointageModal pour réduire la complexité
 */

import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import { logger } from '../../services/logger'
import type { Pointage, PointageCreate, PointageUpdate } from '../../types'

interface UsePointageFormProps {
  isOpen: boolean
  pointage: Pointage | null
  selectedDate?: Date
  selectedUserId?: number
  selectedChantierId?: number
  onSave: (data: PointageCreate | PointageUpdate) => Promise<void>
  onDelete?: () => Promise<void>
  onSign?: (signature: string) => Promise<void>
  onSubmit?: () => Promise<void>
  onValidate?: () => Promise<void>
  onReject?: (motif: string) => Promise<void>
  onClose: () => void
}

export function usePointageForm({
  isOpen,
  pointage,
  selectedDate,
  selectedUserId,
  selectedChantierId,
  onSave,
  onDelete,
  onSign,
  onSubmit,
  onValidate,
  onReject,
  onClose,
}: UsePointageFormProps) {
  const [chantierId, setChantierId] = useState<number | ''>('')
  const [heuresNormales, setHeuresNormales] = useState('07:00')
  const [heuresSupplementaires, setHeuresSupplementaires] = useState('00:00')
  const [commentaire, setCommentaire] = useState('')
  const [signature, setSignature] = useState('')
  const [motifRejet, setMotifRejet] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [showRejectForm, setShowRejectForm] = useState(false)

  const isEditing = !!pointage
  const isEditable = !pointage || pointage.statut === 'brouillon' || pointage.statut === 'rejete'

  useEffect(() => {
    if (isOpen) {
      if (pointage) {
        setChantierId(pointage.chantier_id)
        setHeuresNormales(pointage.heures_normales || '07:00')
        setHeuresSupplementaires(pointage.heures_supplementaires || '00:00')
        setCommentaire(pointage.commentaire || '')
        setSignature('')
        setMotifRejet('')
      } else {
        setChantierId(selectedChantierId || '')
        setHeuresNormales('07:00')
        setHeuresSupplementaires('00:00')
        setCommentaire('')
        setSignature('')
        setMotifRejet('')
      }
      setError('')
      setShowRejectForm(false)
    }
  }, [isOpen, pointage, selectedChantierId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!chantierId) {
      setError('Veuillez selectionner un chantier')
      return
    }

    setSaving(true)
    setError('')

    try {
      if (isEditing) {
        await onSave({
          heures_normales: heuresNormales,
          heures_supplementaires: heuresSupplementaires,
          commentaire: commentaire || undefined,
        } as PointageUpdate)
      } else {
        if (!selectedUserId || !selectedDate) {
          setError('Utilisateur et date requis')
          return
        }
        await onSave({
          utilisateur_id: selectedUserId,
          chantier_id: Number(chantierId),
          date_pointage: format(selectedDate, 'yyyy-MM-dd'),
          heures_normales: heuresNormales,
          heures_supplementaires: heuresSupplementaires,
          commentaire: commentaire || undefined,
        } as PointageCreate)
      }
      onClose()
    } catch (err) {
      setError("Erreur lors de l'enregistrement")
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete) return
    if (!confirm('Supprimer ce pointage ?')) return

    setSaving(true)
    try {
      await onDelete()
      onClose()
    } catch (err) {
      setError('Erreur lors de la suppression')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleSign = async () => {
    if (!onSign || !signature.trim()) {
      setError('Veuillez saisir votre signature')
      return
    }

    setSaving(true)
    try {
      await onSign(signature.trim())
      onClose()
    } catch (err) {
      setError('Erreur lors de la signature')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleSubmitForValidation = async () => {
    if (!onSubmit) return

    setSaving(true)
    try {
      await onSubmit()
      onClose()
    } catch (err) {
      setError('Erreur lors de la soumission')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleValidate = async () => {
    if (!onValidate) return

    setSaving(true)
    try {
      await onValidate()
      onClose()
    } catch (err) {
      setError('Erreur lors de la validation')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleReject = async () => {
    if (!onReject || !motifRejet.trim()) {
      setError('Veuillez saisir un motif de rejet')
      return
    }

    setSaving(true)
    try {
      await onReject(motifRejet.trim())
      onClose()
    } catch (err) {
      setError('Erreur lors du rejet')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  return {
    // State
    chantierId,
    setChantierId,
    heuresNormales,
    setHeuresNormales,
    heuresSupplementaires,
    setHeuresSupplementaires,
    commentaire,
    setCommentaire,
    signature,
    setSignature,
    motifRejet,
    setMotifRejet,
    saving,
    error,
    showRejectForm,
    setShowRejectForm,
    // Computed
    isEditing,
    isEditable,
    // Handlers
    handleSubmit,
    handleDelete,
    handleSign,
    handleSubmitForValidation,
    handleValidate,
    handleReject,
  }
}
