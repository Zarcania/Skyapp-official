// Composant Gestion des Équipes - Assigner collaborateurs aux chefs d'équipe
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, UserPlus, UserMinus, X, AlertCircle, Check } from 'lucide-react';

const API = process.env.REACT_APP_API_BASE_URL || `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api`;

const TeamManagementComponent = () => {
  const [teamLeaders, setTeamLeaders] = useState([]);
  const [availableCollaborators, setAvailableCollaborators] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTeamLeader, setSelectedTeamLeader] = useState(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignForm, setAssignForm] = useState({
    collaborator_id: '',
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Charger chefs d'équipe avec stats + collaborateurs disponibles
      const [leadersRes, usersRes] = await Promise.all([
        axios.get(`${API}/team-leaders-stats`, { headers }),
        axios.get(`${API}/users`, { headers }).catch(() => ({ data: [] }))
      ]);

      setTeamLeaders(leadersRes.data || []);
      
      // Filtrer techniciens non assignés
      const technicians = (usersRes.data || []).filter(u => u.role === 'TECHNICIEN');
      setAvailableCollaborators(technicians);
      
      setLoading(false);
    } catch (error) {
      console.error('Erreur chargement:', error);
      setLoading(false);
    }
  };

  const handleAssignCollaborator = async () => {
    if (!assignForm.collaborator_id) {
      alert('Veuillez sélectionner un collaborateur');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.post(`${API}/team-leaders/assign`, {
        team_leader_id: selectedTeamLeader.id,
        collaborator_id: assignForm.collaborator_id,
        notes: assignForm.notes
      }, { headers });

      setShowAssignModal(false);
      setAssignForm({ collaborator_id: '', notes: '' });
      loadData();
    } catch (error) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('Maximum 10')) {
        alert('⚠️ Maximum 10 collaborateurs par chef d\'équipe atteint');
      } else {
        console.error('Erreur assignation:', error);
        alert('Erreur lors de l\'assignation');
      }
    }
  };

  const handleRemoveCollaborator = async (teamLeaderId, collaboratorId) => {
    if (!window.confirm('Retirer ce collaborateur de l\'équipe?')) return;

    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.delete(`${API}/team-leaders/${teamLeaderId}/collaborators/${collaboratorId}`, { headers });
      loadData();
    } catch (error) {
      console.error('Erreur suppression:', error);
    }
  };

  const openAssignModal = (teamLeader) => {
    setSelectedTeamLeader(teamLeader);
    setShowAssignModal(true);
  };

  const getAvailableCollaboratorsForTeam = (teamLeader) => {
    // Tous les collaborateurs déjà assignés (à TOUS les chefs)
    const allAssignedIds = teamLeaders.flatMap(tl => 
      (tl.collaborators || []).map(c => c.id)
    );
    // Retourner les techniciens qui ne sont assignés à AUCUN chef
    return availableCollaborators.filter(c => !allAssignedIds.includes(c.id));
  };

  const getUnassignedCollaborators = () => {
    // Tous les collaborateurs assignés (tous chefs confondus)
    const allAssignedIds = teamLeaders.flatMap(tl => 
      (tl.collaborators || []).map(c => c.id)
    );
    // Retourner les techniciens non assignés à aucun chef
    return availableCollaborators.filter(c => !allAssignedIds.includes(c.id));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Gestion des Équipes</h1>
        <p className="text-gray-600 mt-1">Assignez jusqu'à 10 collaborateurs par chef d'équipe</p>
      </div>

      {/* Collaborateurs non assignés */}
      {getUnassignedCollaborators().length > 0 && (
        <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-yellow-900">
                {getUnassignedCollaborators().length} collaborateur(s) non assigné(s)
              </h3>
              <div className="mt-2 flex flex-wrap gap-2">
                {getUnassignedCollaborators().map(collab => (
                  <div key={collab.id} className="inline-flex items-center gap-2 bg-white rounded-lg px-3 py-2 border border-yellow-300">
                    <span className="text-sm font-medium text-gray-900">
                      {collab.first_name} {collab.last_name}
                    </span>
                    <span className="text-xs text-gray-500">{collab.email}</span>
                  </div>
                ))}
              </div>
              <p className="text-sm text-yellow-700 mt-2">
                💡 Cliquez sur "Ajouter un collaborateur" sur une carte de chef d'équipe pour les assigner
              </p>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Chargement...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {teamLeaders.map(teamLeader => {
            const collaboratorsCount = teamLeader.collaborators_count || 0;
            const isMaxReached = collaboratorsCount >= 10;
            const available = getAvailableCollaboratorsForTeam(teamLeader);

            return (
              <div key={teamLeader.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                {/* Header carte */}
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                        <Users className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">
                          {teamLeader.name || `${teamLeader.first_name} ${teamLeader.last_name}`}
                        </h3>
                        <p className="text-blue-100 text-sm">{teamLeader.email}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="p-4 bg-blue-50 border-b">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Collaborateurs assignés</span>
                    <span className={`font-bold text-lg ${isMaxReached ? 'text-red-600' : 'text-blue-600'}`}>
                      {collaboratorsCount} / 10
                    </span>
                  </div>
                  {isMaxReached && (
                    <div className="mt-2 flex items-center gap-2 text-red-600 text-xs">
                      <AlertCircle className="w-4 h-4" />
                      Maximum atteint
                    </div>
                  )}
                </div>

                {/* Liste collaborateurs */}
                <div className="p-4 max-h-64 overflow-y-auto">
                  {(teamLeader.collaborators || []).length === 0 ? (
                    <p className="text-gray-500 text-sm text-center py-4">Aucun collaborateur assigné</p>
                  ) : (
                    <div className="space-y-2">
                      {teamLeader.collaborators.map(collab => (
                        <div key={collab.id} className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-blue-700 font-medium text-xs">
                                {collab.first_name?.[0]}{collab.last_name?.[0]}
                              </span>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {collab.first_name} {collab.last_name}
                              </p>
                              <p className="text-xs text-gray-500">{collab.email}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleRemoveCollaborator(teamLeader.id, collab.id)}
                            className="p-1 hover:bg-red-100 rounded text-red-600"
                            title="Retirer"
                          >
                            <UserMinus className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Bouton ajouter */}
                <div className="p-4 border-t">
                  <button
                    onClick={() => openAssignModal(teamLeader)}
                    disabled={isMaxReached || available.length === 0}
                    className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition ${
                      isMaxReached || available.length === 0
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    <UserPlus className="w-4 h-4" />
                    {available.length === 0 ? 'Aucun collaborateur disponible' : 'Ajouter un collaborateur'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal assignation */}
      {showAssignModal && selectedTeamLeader && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Ajouter un collaborateur</h2>
              <button
                onClick={() => { setShowAssignModal(false); setAssignForm({ collaborator_id: '', notes: '' }); }}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-4 p-3 bg-blue-50 rounded">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Chef d'équipe:</span>{' '}
                {selectedTeamLeader.name || `${selectedTeamLeader.first_name} ${selectedTeamLeader.last_name}`}
              </p>
              <p className="text-xs text-gray-600 mt-1">
                {selectedTeamLeader.collaborators_count || 0} / 10 collaborateurs
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Collaborateur</label>
                <select
                  value={assignForm.collaborator_id}
                  onChange={(e) => setAssignForm(prev => ({ ...prev, collaborator_id: e.target.value }))}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Sélectionner un collaborateur</option>
                  {getAvailableCollaboratorsForTeam(selectedTeamLeader).map(collab => (
                    <option key={collab.id} value={collab.id}>
                      {collab.first_name} {collab.last_name} - {collab.email}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Notes (optionnel)</label>
                <textarea
                  value={assignForm.notes}
                  onChange={(e) => setAssignForm(prev => ({ ...prev, notes: e.target.value }))}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Compétences spécifiques, remarques..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => { setShowAssignModal(false); setAssignForm({ collaborator_id: '', notes: '' }); }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={handleAssignCollaborator}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center justify-center gap-2"
                >
                  <Check className="w-4 h-4" />
                  Assigner
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamManagementComponent;
