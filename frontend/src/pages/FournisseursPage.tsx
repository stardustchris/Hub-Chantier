/**
 * FournisseursPage - Page dediee a la gestion des fournisseurs (FIN-14)
 */

import Layout from '../components/Layout'
import FournisseursList from '../components/financier/FournisseursList'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export default function FournisseursPage() {
  useDocumentTitle('Fournisseurs')
  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Fournisseurs</h1>
          <p className="text-gray-500 mt-1">
            Gerez les fournisseurs, sous-traitants et prestataires de services.
          </p>
        </div>

        <FournisseursList />
      </div>
    </Layout>
  )
}
