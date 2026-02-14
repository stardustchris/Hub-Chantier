/**
 * DevisPreviewPage - Apercu PDF du devis (vue client, impression)
 * Ouverte dans un nouvel onglet via le bouton "Apercu PDF"
 */

import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { devisService } from '../services/devis'
import { formatEUR } from '../utils/format'
import type { DevisDetail, LotDevis, LigneDevis } from '../types'
import { Loader2, Printer } from 'lucide-react'

const formatDate = (d: string | null | undefined) => {
  if (!d) return '-'
  const date = new Date(d)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export default function DevisPreviewPage() {
  const { id } = useParams<{ id: string }>()
  const [devis, setDevis] = useState<DevisDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await devisService.getDevis(Number(id))
        setDevis(data)
      } catch (error) {
        console.error('Erreur lors du chargement du devis pour aperçu PDF:', error)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  if (!devis) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-600">Devis introuvable</p>
      </div>
    )
  }

  const totalHT = Number(devis.montant_total_ht || 0)
  const totalTTC = Number(devis.montant_total_ttc || 0)
  const acomptePct = Number(devis.acompte_pct || 0)
  const acompteAmount = totalTTC * acomptePct / 100
  const retenuePct = Number(devis.retenue_garantie_pct || 0)
  const retenueAmount = totalTTC * retenuePct / 100

  return (
    <>
      {/* Print button - hidden in print */}
      <div className="print:hidden fixed top-4 right-4 z-50">
        <button
          onClick={() => window.print()}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg shadow-lg hover:bg-indigo-700"
        >
          <Printer className="w-4 h-4" />
          Imprimer / PDF
        </button>
      </div>

      <div className="max-w-[210mm] mx-auto bg-white p-10 print:p-6 min-h-screen text-sm text-gray-900">
        {/* Header entreprise */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-2xl font-bold text-indigo-600">Greg Constructions</h1>
            <p className="text-gray-500 text-xs mt-1">
              15 Rue des Batisseurs, 75000 Paris<br />
              Tel: 01 23 45 67 89 — SIRET: 123 456 789 00012
            </p>
          </div>
          <div className="text-right">
            <h2 className="text-xl font-bold text-gray-900">DEVIS</h2>
            <p className="text-gray-600 font-medium">{devis.numero}</p>
            <p className="text-gray-500 text-xs mt-1">
              Emis le {formatDate(devis.date_creation)}<br />
              Valable jusqu'au {formatDate(devis.date_validite)}
            </p>
          </div>
        </div>

        {/* Client info */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Client</p>
          <p className="font-semibold">{devis.client_nom}</p>
          {devis.client_adresse && <p className="text-gray-600 text-xs">{devis.client_adresse}</p>}
          {devis.client_email && <p className="text-gray-600 text-xs">{devis.client_email}</p>}
        </div>

        {/* Objet */}
        <div className="mb-6">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Objet</p>
          <p className="font-semibold text-base">{devis.objet}</p>
        </div>

        {/* Table devis */}
        <table className="w-full mb-6 border-collapse">
          <thead>
            <tr className="bg-indigo-600 text-white text-xs">
              <th className="px-3 py-2 text-left w-10">N</th>
              <th className="px-3 py-2 text-left">Designation</th>
              <th className="px-3 py-2 text-right w-16">Qte</th>
              <th className="px-3 py-2 text-center w-12">Unite</th>
              <th className="px-3 py-2 text-right w-20">P.U. HT</th>
              <th className="px-3 py-2 text-center w-14">TVA</th>
              <th className="px-3 py-2 text-right w-24">Total HT</th>
            </tr>
          </thead>
          <tbody>
            {devis.lots.map((lot: LotDevis) => (
              <LotPreview key={lot.id} lot={lot} />
            ))}
          </tbody>
        </table>

        {/* Totaux */}
        <div className="flex justify-end mb-6">
          <div className="w-72">
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Total HT</span>
                <span className="font-medium">{formatEUR(totalHT)}</span>
              </div>

              {devis.ventilation_tva?.map((v, i) => (
                <div key={i} className="flex justify-between text-xs text-gray-500">
                  <span>TVA {v.taux}%</span>
                  <span>{formatEUR(Number(v.montant_tva))}</span>
                </div>
              ))}

              <div className="flex justify-between border-t border-gray-200 pt-2 font-bold text-base">
                <span>Total TTC</span>
                <span>{formatEUR(totalTTC)}</span>
              </div>

              {acomptePct > 0 && (
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Acompte ({acomptePct}%)</span>
                  <span>{formatEUR(acompteAmount)}</span>
                </div>
              )}

              {retenuePct > 0 && (
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Retenue de garantie ({retenuePct}%)</span>
                  <span>- {formatEUR(retenueAmount)}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Conditions */}
        <div className="border-t border-gray-200 pt-4 mb-6 text-xs text-gray-600 space-y-2">
          {devis.echeance && (
            <p><span className="font-medium text-gray-700">Echeance :</span> {
              devis.echeance === 'reception' ? 'Paiement a reception' :
              devis.echeance === '30_jours_fin_mois' ? '30 jours fin de mois' :
              devis.echeance === '45_jours_fin_mois' ? '45 jours fin de mois' :
              devis.echeance === '60_jours' ? '60 jours' : devis.echeance
            }</p>
          )}
          {acomptePct > 0 && (
            <p><span className="font-medium text-gray-700">Acompte :</span> {acomptePct}% a la commande, soit {formatEUR(acompteAmount)}</p>
          )}
          {(devis.notes_bas_page || devis.conditions_generales) && (
            <p className="whitespace-pre-line">{devis.notes_bas_page || devis.conditions_generales}</p>
          )}
        </div>

        {/* Mention legale */}
        {devis.mention_tva_reduite && (
          <div className="bg-amber-50 border border-amber-200 rounded p-3 mb-6 text-xs text-amber-800">
            {devis.mention_tva_reduite}
          </div>
        )}

        {/* Signature */}
        <div className="grid grid-cols-2 gap-8 mt-8 pt-6 border-t border-gray-200">
          <div>
            <p className="text-xs text-gray-500 mb-12">Greg Constructions</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-2">
              Bon pour accord, le client :<br />
              Date et signature precedees de la mention "Bon pour accord"
            </p>
            <div className="h-20 border border-dashed border-gray-300 rounded" />
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 pt-4 border-t border-gray-100 text-center text-[10px] text-gray-600">
          Greg Constructions — SAS au capital de 50 000 EUR — SIRET 123 456 789 00012 — TVA FR12 345678901
        </div>
      </div>
    </>
  )
}

function LotPreview({ lot }: { lot: LotDevis }) {
  return (
    <>
      {/* Lot header */}
      <tr className="bg-indigo-50">
        <td colSpan={6} className="px-3 py-2 font-semibold text-indigo-900 text-xs">
          {lot.numero}. {lot.titre}
        </td>
        <td className="px-3 py-2 text-right font-semibold text-indigo-900 text-xs">
          {formatEUR(Number(lot.total_ht))}
        </td>
      </tr>
      {/* Lines */}
      {lot.lignes.map((ligne: LigneDevis) => (
        <tr key={ligne.id} className="border-b border-gray-100">
          <td className="px-3 py-1.5 text-gray-600 text-xs">{lot.numero}.{ligne.ordre}</td>
          <td className="px-3 py-1.5 text-xs">{ligne.designation}</td>
          <td className="px-3 py-1.5 text-right text-xs">{Number(ligne.quantite)}</td>
          <td className="px-3 py-1.5 text-center text-gray-500 text-xs">{ligne.unite}</td>
          <td className="px-3 py-1.5 text-right text-xs">{formatEUR(Number(ligne.prix_unitaire_ht))}</td>
          <td className="px-3 py-1.5 text-center text-xs text-gray-500">{Number(ligne.taux_tva)}%</td>
          <td className="px-3 py-1.5 text-right font-medium text-xs">{formatEUR(Number(ligne.montant_ht))}</td>
        </tr>
      ))}
    </>
  )
}
