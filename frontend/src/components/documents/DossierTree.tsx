/**
 * Composant DossierTree - Arborescence des dossiers (GED-02)
 */

import React, { useState } from 'react';
import type { DossierTree as DossierTreeType, NiveauAcces } from '../../types/documents';
import { NIVEAU_ACCES_LABELS } from '../../types/documents';
import {
  Folder,
  FolderOpen,
  Pencil,
  Camera,
  FileText,
  Package,
  ShieldCheck,
  ClipboardCheck,
  Lock,
  LockKeyhole,
  HardHat,
  Users,
  Plus,
  Edit,
  Trash2
} from 'lucide-react';

interface DossierTreeProps {
  dossiers: DossierTreeType[];
  selectedDossierId: number | null;
  onSelectDossier: (dossier: DossierTreeType) => void;
  onCreateDossier?: (parentId: number | null) => void;
  onEditDossier?: (dossier: DossierTreeType) => void;
  onDeleteDossier?: (dossier: DossierTreeType) => void;
  userRole?: string;
}

interface DossierNodeProps {
  dossier: DossierTreeType;
  level: number;
  selectedDossierId: number | null;
  onSelectDossier: (dossier: DossierTreeType) => void;
  onCreateDossier?: (parentId: number | null) => void;
  onEditDossier?: (dossier: DossierTreeType) => void;
  onDeleteDossier?: (dossier: DossierTreeType) => void;
  userRole?: string;
}

const DossierNode: React.FC<DossierNodeProps> = ({
  dossier,
  level,
  selectedDossierId,
  onSelectDossier,
  onCreateDossier,
  onEditDossier,
  onDeleteDossier,
  userRole,
}) => {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const hasChildren = dossier.children && dossier.children.length > 0;
  const isSelected = selectedDossierId === dossier.id;

  const getNiveauAccesColor = (niveau: NiveauAcces): string => {
    const colors: Record<NiveauAcces, string> = {
      compagnon: 'bg-green-100 text-green-800',
      chef_chantier: 'bg-blue-100 text-blue-800',
      conducteur: 'bg-yellow-100 text-yellow-800',
      admin: 'bg-red-100 text-red-800',
    };
    return colors[niveau] || 'bg-gray-100 text-gray-800';
  };

  const getFolderIcon = () => {
    const iconClass = "w-4 h-4";
    if (dossier.type_dossier === '01_plans') return <Pencil className={iconClass} />;
    if (dossier.type_dossier === '02_administratif') return <ClipboardCheck className={iconClass} />;
    if (dossier.type_dossier === '03_securite') return <ShieldCheck className={iconClass} />;
    if (dossier.type_dossier === '04_qualite') return <ClipboardCheck className={iconClass} />;
    if (dossier.type_dossier === '05_photos') return <Camera className={iconClass} />;
    if (dossier.type_dossier === '06_comptes_rendus') return <FileText className={iconClass} />;
    if (dossier.type_dossier === '07_livraisons') return <Package className={iconClass} />;
    return isSelected ? <FolderOpen className={iconClass} /> : <Folder className={iconClass} />;
  };

  return (
    <div className="select-none">
      <div
        className={`group flex items-center py-2 px-2 rounded cursor-pointer hover:bg-gray-100 transition-colors ${
          isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : ''
        }`}
        style={{ paddingLeft: `${level * 20 + 8}px` }}
        onClick={() => onSelectDossier(dossier)}
      >
        {/* Chevron */}
        <button
          className="w-5 h-5 flex items-center justify-center mr-1"
          onClick={(e) => {
            e.stopPropagation();
            setIsExpanded(!isExpanded);
          }}
        >
          {hasChildren && (
            <span className="text-gray-500">{isExpanded ? '▼' : '▶'}</span>
          )}
        </button>

        {/* Icon */}
        <span className="mr-2 text-gray-600">{getFolderIcon()}</span>

        {/* Nom */}
        <span className="flex-1 font-medium truncate">{dossier.nom}</span>

        {/* Badge niveau d'accès */}
        <span
          className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${getNiveauAccesColor(
            dossier.niveau_acces
          )}`}
          title={NIVEAU_ACCES_LABELS[dossier.niveau_acces]}
        >
          {dossier.niveau_acces === 'admin' ? (
            <><Lock className="w-3 h-3" /><span className="hidden sm:inline">Admin</span></>
          ) : dossier.niveau_acces === 'conducteur' ? (
            <><LockKeyhole className="w-3 h-3" /><span className="hidden sm:inline">Cond.</span></>
          ) : dossier.niveau_acces === 'chef_chantier' ? (
            <><HardHat className="w-3 h-3" /><span className="hidden sm:inline">Chef</span></>
          ) : (
            <><Users className="w-3 h-3" /><span className="hidden sm:inline">Tous</span></>
          )}
        </span>

        {/* Compteur documents */}
        {dossier.nombre_documents > 0 && (
          <span className="ml-2 text-xs text-gray-600 bg-gray-100 px-2 py-0.5 rounded-full">
            {dossier.nombre_documents}
          </span>
        )}

        {/* Actions */}
        {(onEditDossier || onDeleteDossier || onCreateDossier) && (
          <div className="ml-2 flex gap-1 opacity-0 group-hover:opacity-100">
            {onCreateDossier && (
              <button
                className="p-1 text-gray-600 hover:text-blue-500 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  onCreateDossier(dossier.id);
                }}
                title="Créer un sous-dossier"
              >
                <Plus className="w-4 h-4" />
              </button>
            )}
            {onEditDossier && (
              <button
                className="p-1 text-gray-600 hover:text-blue-500 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  onEditDossier(dossier);
                }}
                title="Modifier"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}
            {onDeleteDossier && dossier.type_dossier === 'custom' && (
              <button
                className="p-1 text-gray-600 hover:text-red-500 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteDossier(dossier);
                }}
                title="Supprimer"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Children */}
      {isExpanded && hasChildren && (
        <div>
          {dossier.children.map((child) => (
            <DossierNode
              key={child.id}
              dossier={child}
              level={level + 1}
              selectedDossierId={selectedDossierId}
              onSelectDossier={onSelectDossier}
              onCreateDossier={onCreateDossier}
              onEditDossier={onEditDossier}
              onDeleteDossier={onDeleteDossier}
              userRole={userRole}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const DossierTree: React.FC<DossierTreeProps> = ({
  dossiers,
  selectedDossierId,
  onSelectDossier,
  onCreateDossier,
  onEditDossier,
  onDeleteDossier,
  userRole,
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-700">Dossiers</h3>
        {onCreateDossier && (
          <button
            className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
            onClick={() => onCreateDossier(null)}
          >
            + Nouveau
          </button>
        )}
      </div>

      <div className="space-y-1">
        {dossiers.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-4">
            Aucun dossier. Cliquez sur "Nouveau" pour créer le premier.
          </p>
        ) : (
          dossiers.map((dossier) => (
            <DossierNode
              key={dossier.id}
              dossier={dossier}
              level={0}
              selectedDossierId={selectedDossierId}
              onSelectDossier={onSelectDossier}
              onCreateDossier={onCreateDossier}
              onEditDossier={onEditDossier}
              onDeleteDossier={onDeleteDossier}
              userRole={userRole}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default DossierTree;
