// Composant Mes Missions - Vue Technicien (Lecture seule)
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Calendar, Clock, MapPin, AlertCircle, CheckCircle, Loader, 
  X, FileText, Image as ImageIcon, Eye, ChevronRight, User, Building 
} from 'lucide-react';

const API = process.env.REACT_APP_API_BASE_URL || `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api`;

const MesMissionsComponent = () => {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, scheduled: 0, in_progress: 0, completed: 0 });
  const [filter, setFilter] = useState({ status: 'all', from: '', to: '' });
  const [user, setUser] = useState(null);
  const [selectedMission, setSelectedMission] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [missionDetails, setMissionDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    loadUserAndMissions();
  }, [filter]);

  const loadUserAndMissions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Récupérer l'utilisateur connecté
      const userRes = await axios.get(`${API}/auth/me`, { headers });
      const currentUser = userRes.data;
      setUser(currentUser);

      // Construire l'URL avec filtres
      let url = `${API}/technicians/${currentUser.id}/missions`;
      const params = new URLSearchParams();
      if (filter.from) params.append('from', filter.from);
      if (filter.to) params.append('to', filter.to);
      if (filter.status !== 'all') params.append('status', filter.status);
      if (params.toString()) url += `?${params.toString()}`;

      // Charger les missions
      const res = await axios.get(url, { headers });
      const missionsData = res.data || [];
      setMissions(missionsData);

      // Calculer stats
      setStats({
        total: missionsData.length,
        scheduled: missionsData.filter(m => m.status === 'scheduled').length,
        in_progress: missionsData.filter(m => m.status === 'in_progress').length,
        completed: missionsData.filter(m => m.status === 'completed').length,
      });

      setLoading(false);
    } catch (error) {
      console.error('Erreur chargement missions:', error);
      setLoading(false);
    }
  };

  const loadMissionDetails = async (missionId) => {
    try {
      setLoadingDetails(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Charger les détails de la mission avec worksite, photos, et quote
      const missionRes = await axios.get(`${API}/schedules/${missionId}`, { headers });
      const mission = missionRes.data;

      // Charger le worksite complet avec photos
      let worksiteDetails = null;
      if (mission.worksite_id) {
        try {
          const worksiteRes = await axios.get(`${API}/worksites/${mission.worksite_id}`, { headers });
          worksiteDetails = worksiteRes.data;
        } catch (error) {
          console.error('Erreur chargement worksite:', error);
        }
      }

      // Charger le devis lié au chantier
      let quoteDetails = null;
      if (worksiteDetails?.quote_id) {
        try {
          const quoteRes = await axios.get(`${API}/quotes/${worksiteDetails.quote_id}`, { headers });
          quoteDetails = quoteRes.data;
        } catch (error) {
          console.error('Erreur chargement devis:', error);
        }
      }

      setMissionDetails({
        ...mission,
        worksite: worksiteDetails,
        quote: quoteDetails
      });
      setLoadingDetails(false);
    } catch (error) {
      console.error('Erreur chargement détails mission:', error);
      setLoadingDetails(false);
    }
  };

  const openMissionDetail = (mission) => {
    setSelectedMission(mission);
    setShowDetailModal(true);
    loadMissionDetails(mission.id);
  };

  const getStatusBadge = (status) => {
    const styles = {
      scheduled: 'bg-blue-100 text-blue-800 border border-blue-200',
      in_progress: 'bg-orange-100 text-orange-800 border border-orange-200',
      completed: 'bg-green-100 text-green-800 border border-green-200',
      cancelled: 'bg-gray-100 text-gray-800 border border-gray-200',
    };
    const labels = {
      scheduled: '🗓️ Planifiée',
      in_progress: '⚙️ En cours',
      completed: '✅ Terminée',
      cancelled: '❌ Annulée',
    };
    return (
      <span className={`px-4 py-1.5 rounded-full text-sm font-semibold ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
        {labels[status] || status}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      {/* Header amélioré */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-3 rounded-2xl shadow-lg">
            <Calendar className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Mes Missions
            </h1>
            <p className="text-gray-600 flex items-center gap-2">
              <User className="w-4 h-4" />
              {user?.first_name} {user?.last_name}
            </p>
          </div>
        </div>
      </div>

      {/* Stats Cards modernisées */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-5 rounded-2xl shadow-md hover:shadow-xl transition-all border-2 border-gray-100 hover:border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <div className="bg-gray-100 p-3 rounded-xl">
              <Calendar className="w-6 h-6 text-gray-600" />
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
          <p className="text-sm font-semibold text-gray-600">Total Missions</p>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-5 rounded-2xl shadow-md hover:shadow-xl transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="bg-white/20 p-3 rounded-xl backdrop-blur-sm">
              <Clock className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-white">{stats.scheduled}</p>
            </div>
          </div>
          <p className="text-sm font-semibold text-blue-100">Planifiées</p>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-5 rounded-2xl shadow-md hover:shadow-xl transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="bg-white/20 p-3 rounded-xl backdrop-blur-sm">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-white">{stats.in_progress}</p>
            </div>
          </div>
          <p className="text-sm font-semibold text-orange-100">En Cours</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 p-5 rounded-2xl shadow-md hover:shadow-xl transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="bg-white/20 p-3 rounded-xl backdrop-blur-sm">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-white">{stats.completed}</p>
            </div>
          </div>
          <p className="text-sm font-semibold text-green-100">Terminées</p>
        </div>
      </div>

      {/* Filtres modernisés */}
      <div className="bg-white/80 backdrop-blur-xl p-5 rounded-2xl shadow-md mb-6 border border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="bg-blue-100 p-2 rounded-lg">
            <span className="text-lg">🔍</span>
          </div>
          <h2 className="text-lg font-bold text-gray-900">Filtres</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wide">Statut</label>
            <select
              value={filter.status}
              onChange={(e) => setFilter(prev => ({ ...prev, status: e.target.value }))}
              className="w-full rounded-xl border-2 border-gray-200 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white transition-all"
            >
              <option value="all">Tous les statuts</option>
              <option value="scheduled">Planifiées</option>
              <option value="in_progress">En cours</option>
              <option value="completed">Terminées</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wide">Date début</label>
            <input
              type="date"
              value={filter.from}
              onChange={(e) => setFilter(prev => ({ ...prev, from: e.target.value }))}
              className="w-full rounded-xl border-2 border-gray-200 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white transition-all"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wide">Date fin</label>
            <input
              type="date"
              value={filter.to}
              onChange={(e) => setFilter(prev => ({ ...prev, to: e.target.value }))}
              className="w-full rounded-xl border-2 border-gray-200 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white transition-all"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setFilter({ status: 'all', from: '', to: '' })}
              className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl text-gray-700 font-semibold text-sm shadow-sm transition-all"
            >
              Réinitialiser
            </button>
          </div>
        </div>
      </div>

      {/* Liste des missions - Design professionnel */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {missions.length === 0 ? (
          <div className="p-16 text-center">
            <div className="bg-gray-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-lg font-semibold text-gray-700 mb-1">Aucune mission assignée</p>
            <p className="text-sm text-gray-500">Vos missions apparaîtront ici</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {missions.map((mission) => {
              const statusConfig = {
                scheduled: { 
                  color: 'bg-blue-50 text-blue-700 border-blue-200', 
                  dot: 'bg-blue-500',
                  label: 'Planifiée' 
                },
                in_progress: { 
                  color: 'bg-orange-50 text-orange-700 border-orange-200', 
                  dot: 'bg-orange-500',
                  label: 'En cours' 
                },
                completed: { 
                  color: 'bg-green-50 text-green-700 border-green-200', 
                  dot: 'bg-green-500',
                  label: 'Terminée' 
                },
              };
              const config = statusConfig[mission.status] || statusConfig.scheduled;

              return (
                <div 
                  key={mission.id} 
                  className="group hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => openMissionDetail(mission)}
                >
                  <div className="p-6">
                    <div className="flex items-start gap-6">
                      {/* Date block - Format calendrier avec période */}
                      <div className="flex-shrink-0 text-center">
                        <div className="bg-gray-100 rounded-lg p-3 min-w-[70px]">
                          {(() => {
                            const startDate = new Date(mission.start_date || mission.date);
                            const endDate = new Date(mission.end_date || mission.date || mission.start_date);
                            const isSameDay = startDate.toDateString() === endDate.toDateString();
                            
                            if (isSameDay) {
                              return (
                                <>
                                  <div className="text-2xl font-bold text-gray-900">
                                    {startDate.getDate()}
                                  </div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">
                                    {startDate.toLocaleDateString('fr-FR', { month: 'short' })}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    {startDate.getFullYear()}
                                  </div>
                                </>
                              );
                            } else {
                              return (
                                <>
                                  <div className="text-sm font-bold text-gray-900">
                                    {startDate.getDate()} - {endDate.getDate()}
                                  </div>
                                  <div className="text-xs font-semibold text-gray-600 uppercase">
                                    {startDate.toLocaleDateString('fr-FR', { month: 'short' })}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    {startDate.getFullYear()}
                                  </div>
                                </>
                              );
                            }
                          })()}
                        </div>
                      </div>

                      {/* Contenu principal */}
                      <div className="flex-1 min-w-0">
                        {/* Header avec titre et statut */}
                        <div className="flex items-start justify-between gap-4 mb-3">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                              {mission.worksites?.title || 'Chantier'}
                            </h3>
                            <p className="text-xs text-gray-500 font-mono">
                              Mission #{mission.id?.substring(0, 8).toUpperCase()}
                            </p>
                          </div>
                          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${config.color}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`}></span>
                            {config.label}
                          </span>
                        </div>

                        {/* Informations détaillées en grille */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-3">
                          <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
                            <div className="min-w-0">
                              <p className="text-xs text-gray-500">Horaire</p>
                              <p className="text-sm font-medium text-gray-900">{mission.time} • {mission.hours}h</p>
                            </div>
                          </div>

                          {mission.worksites?.address && (
                            <div className="flex items-center gap-2 sm:col-span-2">
                              <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                              <div className="min-w-0">
                                <p className="text-xs text-gray-500">Lieu</p>
                                <p className="text-sm font-medium text-gray-900 truncate">
                                  {mission.worksites.address}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Description */}
                        {mission.description && (
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {mission.description}
                          </p>
                        )}
                      </div>

                      {/* Action - Voir détails */}
                      <div className="flex-shrink-0 self-center">
                        <button className="p-2 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-all">
                          <Eye className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Modal de détails de la mission */}
      {showDetailModal && selectedMission && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header du modal */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-3xl flex items-center justify-between z-10">
              <div>
                <h2 className="text-3xl font-bold mb-1">📋 Détails de la Mission</h2>
                <p className="text-blue-100">Toutes les informations relatives à votre mission</p>
              </div>
              <button
                onClick={() => {
                  setShowDetailModal(false);
                  setSelectedMission(null);
                  setMissionDetails(null);
                }}
                className="bg-white/20 hover:bg-white/30 rounded-full p-2 transition-all"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Contenu du modal */}
            <div className="p-6">
              {loadingDetails ? (
                <div className="flex items-center justify-center py-12">
                  <Loader className="w-12 h-12 animate-spin text-blue-600" />
                </div>
              ) : missionDetails ? (
                <div className="space-y-6">
                  {/* Informations générales */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border-2 border-blue-200">
                    <h3 className="text-xl font-bold text-blue-900 mb-4">ℹ️ Informations Générales</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-white rounded-xl p-4">
                        <p className="text-sm font-medium text-gray-500 mb-1">Chantier</p>
                        <p className="text-lg font-bold text-gray-900">{missionDetails.worksite?.title || 'N/A'}</p>
                      </div>
                      <div className="bg-white rounded-xl p-4">
                        <p className="text-sm font-medium text-gray-500 mb-1">Date et Heure</p>
                        <p className="text-lg font-bold text-gray-900">
                          {(() => {
                            const startDate = new Date(missionDetails.start_date || missionDetails.date);
                            const endDate = new Date(missionDetails.end_date || missionDetails.date || missionDetails.start_date);
                            const isSameDay = startDate.toDateString() === endDate.toDateString();
                            
                            if (isSameDay) {
                              return `${startDate.toLocaleDateString('fr-FR')} à ${missionDetails.time}`;
                            } else {
                              return `Du ${startDate.toLocaleDateString('fr-FR')} au ${endDate.toLocaleDateString('fr-FR')} à ${missionDetails.time}`;
                            }
                          })()}
                        </p>
                      </div>
                      {missionDetails.worksite?.address && (
                        <div className="bg-white rounded-xl p-4 md:col-span-2">
                          <p className="text-sm font-medium text-gray-500 mb-1">Adresse</p>
                          <p className="text-lg font-bold text-gray-900">{missionDetails.worksite.address}</p>
                        </div>
                      )}
                      {missionDetails.description && (
                        <div className="bg-white rounded-xl p-4 md:col-span-2">
                          <p className="text-sm font-medium text-gray-500 mb-1">Description</p>
                          <p className="text-gray-700">{missionDetails.description}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Photos du chantier */}
                  {missionDetails.worksite?.photos && missionDetails.worksite.photos.length > 0 && (
                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border-2 border-purple-200">
                      <h3 className="text-xl font-bold text-purple-900 mb-4 flex items-center gap-2">
                        <ImageIcon className="w-6 h-6" />
                        Photos du Chantier ({missionDetails.worksite.photos.length})
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {missionDetails.worksite.photos.map((photo, index) => (
                          <div key={index} className="relative group">
                            <img
                              src={photo.url}
                              alt={photo.label || `Photo ${index + 1}`}
                              className="w-full h-40 object-cover rounded-xl shadow-md group-hover:shadow-xl transition-all"
                            />
                            {photo.label && (
                              <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs p-2 rounded-b-xl">
                                {photo.label}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Rapport */}
                  {missionDetails.worksite?.report && (
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border-2 border-green-200">
                      <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center gap-2">
                        <FileText className="w-6 h-6" />
                        Rapport de Mission
                      </h3>
                      <div className="bg-white rounded-xl p-4">
                        <p className="text-gray-700 whitespace-pre-wrap">{missionDetails.worksite.report}</p>
                      </div>
                    </div>
                  )}

                  {/* Devis (sans prix) */}
                  {missionDetails.quote && (
                    <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl p-6 border-2 border-orange-200">
                      <h3 className="text-xl font-bold text-orange-900 mb-4 flex items-center gap-2">
                        <FileText className="w-6 h-6" />
                        Devis Associé
                      </h3>
                      <div className="space-y-4">
                        <div className="bg-white rounded-xl p-4">
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                              <p className="text-sm font-medium text-gray-500">Numéro</p>
                              <p className="text-lg font-bold text-gray-900">{missionDetails.quote.quote_number || 'N/A'}</p>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-500">Client</p>
                              <p className="text-lg font-bold text-gray-900">{missionDetails.quote.client_name || 'N/A'}</p>
                            </div>
                          </div>
                          {missionDetails.quote.items && missionDetails.quote.items.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-gray-700 mb-2">Articles / Services :</p>
                              <div className="space-y-2">
                                {missionDetails.quote.items.map((item, index) => (
                                  <div key={index} className="bg-gray-50 p-3 rounded-lg">
                                    <p className="font-semibold text-gray-900">{item.designation || item.description}</p>
                                    <p className="text-sm text-gray-600">Quantité: {item.quantity || 1}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Impossible de charger les détails de la mission</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MesMissionsComponent;
