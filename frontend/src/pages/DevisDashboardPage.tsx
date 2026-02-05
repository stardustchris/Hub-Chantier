/**
 * DevisDashboardPage - Dashboard pipeline commercial devis
 * Module Devis (Module 20) - DEV-17
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import DevisKanban from '../components/devis/DevisKanban'
import DevisStatusBadge from '../components/devis/DevisStatusBadge'
import { devisService } from '../services/devis'
import type { DashboardDevis, DevisRecent } from '../types'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import {
  Loader2,
  AlertCircle,
  FileText,
  Euro,
  TrendingUp,
  User,
  AlertTriangle,
  Clock,
  Eye,
  MessageSquare,
} from 'lucide-react'

const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

export default function DevisDashboardPage() {
  const navigate = useNavigate()
  const [data, setData] = useState<DashboardDevis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const dashboard = await devisService.getDashboard()
      setData(dashboard)
    } catch {
      setError('Erreur lors du chargement du dashboard devis')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  return (
    <Layout>
      <div className="space-y-6" role="main" aria-label="Dashboard pipeline devis">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Pipeline Commercial</h1>
          {!loading && data && (
            <button
              onClick={loadDashboard}
              className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
            >
              Actualiser
            </button>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
            <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
            <div>
              <p>{error}</p>
              <button onClick={loadDashboard} className="text-sm underline mt-1">Reessayer</button>
            </div>
          </div>
        )}

        {/* Content */}
        {!loading && !error && data && (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" role="region" aria-label="Indicateurs cles">
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Devis en cours</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {data.kpi.nb_envoye + data.kpi.nb_vu + data.kpi.nb_en_negociation + data.kpi.nb_en_validation}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {data.kpi.nb_total} devis au total
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Montant pipeline</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatEUR(Number(data.kpi.total_pipeline_ht))}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Accepte: {formatEUR(Number(data.kpi.total_accepte_ht))}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <Euro className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Taux de conversion</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {Number(data.kpi.taux_conversion).toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {data.kpi.nb_accepte} accepte{data.kpi.nb_accepte > 1 ? 's' : ''} / {data.kpi.nb_refuse} refuse{data.kpi.nb_refuse > 1 ? 's' : ''}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
              </div>
            </div>

            {/* Alertes DEV-17 */}
            <AlertsPanel devis={data.derniers_devis} kpi={data.kpi} />

            {/* Funnel conversion DEV-17 */}
            <ConversionFunnel kpi={data.kpi} />

            {/* Vue Kanban */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6" role="region" aria-label="Vue kanban des devis">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline par statut</h2>
              <DevisKanban
                devis={data.derniers_devis}
                devisParStatut={{
                  brouillon: data.kpi.nb_brouillon,
                  en_validation: data.kpi.nb_en_validation,
                  envoye: data.kpi.nb_envoye,
                  vu: data.kpi.nb_vu,
                  en_negociation: data.kpi.nb_en_negociation,
                  accepte: data.kpi.nb_accepte,
                  refuse: data.kpi.nb_refuse,
                  perdu: data.kpi.nb_perdu,
                  expire: data.kpi.nb_expire,
                }}
              />
            </div>

            {/* Top 5 devis recents */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden" role="region" aria-label="Derniers devis">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Derniers devis</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Numero</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Client</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Objet</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">Montant HT</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Statut</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {data.derniers_devis.slice(0, 5).map((d) => (
                      <tr
                        key={d.id}
                        onClick={() => navigate(`/devis/${d.id}`)}
                        className="hover:bg-gray-50 transition-colors cursor-pointer"
                      >
                        <td className="px-4 py-3 font-mono text-xs text-gray-500">{d.numero}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <User className="w-3.5 h-3.5 text-gray-400" />
                            <span className="font-medium text-gray-900">{d.client_nom}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-700 max-w-xs truncate">{d.objet}</td>
                        <td className="px-4 py-3 text-right font-medium">{formatEUR(Number(d.montant_total_ht))}</td>
                        <td className="px-4 py-3 text-center">
                          <DevisStatusBadge statut={d.statut} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {data.derniers_devis.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto text-gray-300 mb-2" />
                    <p>Aucun devis</p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  )
}

// --- DEV-17: Alerts Panel ---

interface AlertItem {
  icon: typeof AlertTriangle
  color: string
  bgColor: string
  label: string
  count: number
}

function AlertsPanel({ devis, kpi }: { devis: DevisRecent[]; kpi: DashboardDevis['kpi'] }) {
  const now = new Date()
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)

  // Compute alert counts from available data
  const expiringSoon = devis.filter(d => {
    if (d.statut !== 'envoye' && d.statut !== 'vu') return false
    // Assume 30-day validity from creation
    const created = new Date(d.date_creation)
    const expiry = new Date(created.getTime() + 30 * 24 * 60 * 60 * 1000)
    const daysLeft = (expiry.getTime() - now.getTime()) / (24 * 60 * 60 * 1000)
    return daysLeft <= 7 && daysLeft > 0
  }).length

  const pendingValidation = kpi.nb_en_validation

  const notViewedOld = devis.filter(d => {
    if (d.statut !== 'envoye') return false
    const created = new Date(d.date_creation)
    return created < sevenDaysAgo
  }).length

  const longNegotiation = kpi.nb_en_negociation

  const alerts: AlertItem[] = [
    { icon: Clock, color: 'text-amber-600', bgColor: 'bg-amber-50 border-amber-200', label: 'Expiration < 7j', count: expiringSoon },
    { icon: AlertTriangle, color: 'text-orange-600', bgColor: 'bg-orange-50 border-orange-200', label: 'En attente validation', count: pendingValidation },
    { icon: Eye, color: 'text-blue-600', bgColor: 'bg-blue-50 border-blue-200', label: 'Non vu > 7j', count: notViewedOld },
    { icon: MessageSquare, color: 'text-purple-600', bgColor: 'bg-purple-50 border-purple-200', label: 'En negociation', count: longNegotiation },
  ].filter(a => a.count > 0)

  if (alerts.length === 0) return null

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4" role="region" aria-label="Alertes">
      {alerts.map(alert => (
        <div key={alert.label} className={`rounded-xl p-4 border ${alert.bgColor}`}>
          <div className="flex items-center gap-3">
            <alert.icon className={`w-5 h-5 ${alert.color}`} />
            <div>
              <p className="text-2xl font-bold text-gray-900">{alert.count}</p>
              <p className="text-xs text-gray-600">{alert.label}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

// --- DEV-17: Conversion Funnel Chart ---

function ConversionFunnel({ kpi }: { kpi: DashboardDevis['kpi'] }) {
  const funnelData = [
    { name: 'Brouillon', value: kpi.nb_brouillon, color: '#6B7280' },
    { name: 'En validation', value: kpi.nb_en_validation, color: '#F59E0B' },
    { name: 'Envoye', value: kpi.nb_envoye, color: '#3B82F6' },
    { name: 'Vu', value: kpi.nb_vu, color: '#8B5CF6' },
    { name: 'Negociation', value: kpi.nb_en_negociation, color: '#F97316' },
    { name: 'Accepte', value: kpi.nb_accepte, color: '#10B981' },
    { name: 'Refuse', value: kpi.nb_refuse, color: '#EF4444' },
    { name: 'Perdu', value: kpi.nb_perdu, color: '#9CA3AF' },
  ].filter(d => d.value > 0)

  if (funnelData.length === 0) return null

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6" role="region" aria-label="Funnel de conversion">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Funnel de conversion</h2>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={funnelData} layout="vertical" margin={{ left: 80 }}>
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fill: '#6B7280' }} />
            <Tooltip
              formatter={(value) => [`${value} devis`]}
              contentStyle={{ borderRadius: 8, border: '1px solid #E5E7EB' }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={32}>
              {funnelData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
