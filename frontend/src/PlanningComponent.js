import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Calendar, 
  UserPlus, 
  Users, 
  Edit, 
  Trash2, 
  X, 
  Clock,
  CalendarDays,
  CalendarRange,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

// Resolve API base URL consistently with App.js to avoid missing "/api" prefix
// Prefer REACT_APP_BACKEND_URL for host; if REACT_APP_API_BASE_URL is set, use it directly
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = process.env.REACT_APP_API_BASE_URL || `${BACKEND_URL}/api`;

// Simple UI Components
const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-lg border ${className}`}>
    {children}
  </div>
);

const CardContent = ({ children, className = "" }) => (
  <div className={`p-4 ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children, className = "" }) => (
  <div className={`px-4 pt-4 ${className}`}>
    {children}
  </div>
);

const CardTitle = ({ children, className = "" }) => (
  <h3 className={`text-lg font-semibold ${className}`}>
    {children}
  </h3>
);

const Button = ({ children, onClick, variant = "default", size = "default", className = "", disabled = false, ...props }) => {
  const baseClasses = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none";
  
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    outline: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500",
    ghost: "text-gray-700 hover:bg-gray-100 focus:ring-blue-500"
  };
  
  const sizes = {
    sm: "text-sm px-3 py-1.5",
    default: "text-sm px-4 py-2",
    lg: "text-base px-6 py-3"
  };
  
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

const Input = ({ className = "", ...props }) => (
  <input
    className={`flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    {...props}
  />
);

const Badge = ({ children, className = "" }) => (
  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}>
    {children}
  </span>
);

// Planning Management Component - Complete Team and Schedule Management
const PlanningManagement = () => {
  const [teamLeaders, setTeamLeaders] = useState([]);
  const [collaborators, setCollaborators] = useState([]);
  const [worksites, setWorksites] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [acceptedInvites, setAcceptedInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('planning');
  const [showTeamLeaderForm, setShowTeamLeaderForm] = useState(false);
  const [showCollaboratorForm, setShowCollaboratorForm] = useState(false);
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  
  // Vue temporelle - nouveau
  const [viewMode, setViewMode] = useState('week'); // 'day', 'week', 'month'
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // NEW: Enhanced day detail modal state
  const [showDayDetail, setShowDayDetail] = useState(false);
  const [selectedDayData, setSelectedDayData] = useState(null);
  const [detailedDate, setDetailedDate] = useState(null);
  
  // Form states
  const [teamLeaderData, setTeamLeaderData] = useState({
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    specialite: '',
    couleur: '#3B82F6'
  });
  
  const [collaboratorData, setCollaboratorData] = useState({
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    competences: '',
    team_leader_id: ''
  });
  
  const [scheduleData, setScheduleData] = useState({
    worksite_id: '',
    team_leader_id: '',
    collaborator_id: '',
    date: selectedDate,
    time: '08:00', // Heure de début
    shift: 'day', // day, night, morning, afternoon
    hours: '8',
    description: ''
  });

  const SHIFT_OPTIONS = [
    { value: 'day', label: 'Journée complète (8h)', hours: 8 },
    { value: 'morning', label: 'Matinée (4h)', hours: 4 },
    { value: 'afternoon', label: 'Après-midi (4h)', hours: 4 },
    { value: 'night', label: 'Nuit (8h)', hours: 8 }
  ];

  const SPECIALTIES = [
    'Détection de réseaux',
    'Géolocalisation',
    'Travaux publics',
    'Électricité',
    'Plomberie',
    'Maçonnerie',
    'Supervision'
  ];

  const COLORS = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
    '#8B5CF6', '#F97316', '#EC4899', '#06B6D4'
  ];

  useEffect(() => {
    loadPlanningData();
  }, []);

  const loadPlanningData = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Charger les chantiers existants
      const worksitesRes = await axios.get(`${API}/worksites`, { headers });
      setWorksites(worksitesRes.data || []);
      
      // Charger les chefs d'équipe
      try {
        const leadersRes = await axios.get(`${API}/team-leaders`, { headers });
        setTeamLeaders(leadersRes.data || []);
      } catch (error) {
        console.warn('Endpoint team-leaders non disponible, utilisation de données simulées');
        // Données simulées pour les chefs d'équipe
        setTeamLeaders([
          {
            id: '1',
            nom: 'Dupont',
            prenom: 'Jean',
            email: 'jean.dupont@skyapp.fr',
            telephone: '06 12 34 56 78',
            specialite: 'Détection de réseaux',
            couleur: '#3B82F6',
            created_at: '2024-01-15'
          },
          {
            id: '2',
            nom: 'Martin',
            prenom: 'Marie',
            email: 'marie.martin@skyapp.fr',
            telephone: '06 98 76 54 32',
            specialite: 'Géolocalisation',
            couleur: '#EF4444',
            created_at: '2024-01-20'
          }
        ]);
      }

      // Charger les collaborateurs
      try {
        const collabRes = await axios.get(`${API}/collaborators`, { headers });
        setCollaborators(collabRes.data || []);
      } catch (error) {
        console.warn('Endpoint collaborators non disponible, utilisation de données simulées');
        // Données simulées pour les collaborateurs
        setCollaborators([
          {
            id: '1',
            nom: 'Durand',
            prenom: 'Pierre',
            email: 'pierre.durand@skyapp.fr',
            telephone: '06 11 22 33 44',
            competences: 'Assistant détection, Lecture de plans',
            team_leader_id: '1',
            created_at: '2024-01-22'
          },
          {
            id: '2',
            nom: 'Leroux',
            prenom: 'Sophie',
            email: 'sophie.leroux@skyapp.fr',
            telephone: '06 55 66 77 88',
            competences: 'Topographie, GPS',
            team_leader_id: '2',
            created_at: '2024-01-25'
          }
        ]);
      }

      // Charger les invitations acceptées
      await loadAcceptedInvitations();

      // Charger les plannings
      try {
        const schedulesRes = await axios.get(`${API}/schedules`, { headers });
        setSchedules(schedulesRes.data || []);
      } catch (error) {
        console.warn('Endpoint schedules non disponible, utilisation de données simulées');
        // Données simulées pour les plannings
        setSchedules([
          {
            id: '1',
            worksite_id: '1',
            team_leader_id: '1',
            collaborator_id: '1',
            date: selectedDate,
            time: '09:00',
            shift: 'day',
            hours: 8,
            description: 'Inspection complète du site',
            status: 'scheduled',
            created_at: new Date().toISOString()
          }
        ]);
      }

    } catch (error) {
      console.error('Erreur chargement planning:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAcceptedInvitations = async () => {
    try {
      const token = localStorage.getItem('token');
      
      try {
        const invitationsRes = await axios.get(`${API}/invitations/accepted`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setAcceptedInvites(invitationsRes.data);
      } catch (error) {
        console.error('Erreur chargement invitations acceptées:', error);
        // Sample accepted invitations data
        setAcceptedInvites([
          {
            id: '1',
            firstName: 'Marie',
            lastName: 'Dubois',
            email: 'marie.dubois@example.com',
            phone: '06.12.34.56.78',
            role: 'Technicien BTP',
            skills: 'Maçonnerie, Plomberie',
            accepted_at: '2025-01-10T10:00:00Z',
            usedAsTeamLeader: false,
            usedAsCollaborator: false
          },
          {
            id: '2',
            firstName: 'Pierre',
            lastName: 'Martin',
            email: 'pierre.martin@example.com',
            phone: '06.98.76.54.32',
            role: 'Chef de chantier',
            skills: 'Électricité, Coordination équipe',
            accepted_at: '2025-01-08T14:30:00Z',
            usedAsTeamLeader: false,
            usedAsCollaborator: false
          }
        ]);
      }
      
      // Keep the old invitations data for backward compatibility
      const acceptedInvitations = [
        {
          id: 'inv_manager_bureau',
          email: 'manager@bureau.fr',
          nom: 'Manager',
          prenom: 'Bureau',
          role: 'BUREAU',
          status: 'ACCEPTED',
          specialite: 'Gestion de projet',
          competences: 'Management, Planning, Coordination équipes',
          accepted_at: '2024-01-11T09:15:00Z',
          invited_at: '2024-01-10T14:30:00Z'
        },
        {
          id: 'inv_nouveau_tech',
          email: 'nouveau@technicien.fr',
          nom: 'Nouveau',
          prenom: 'Technicien',
          role: 'TECHNICIEN',
          status: 'ACCEPTED',
          specialite: 'Travaux terrain',
          competences: 'Recherche terrain, Mesures, Diagnostics',
          accepted_at: '2024-01-12T10:45:00Z',
          invited_at: '2024-01-15T10:00:00Z'
        }
      ];
      
      setInvitations(acceptedInvitations.filter(inv => inv.status === 'ACCEPTED'));
      console.log('Invitations acceptées chargées:', acceptedInvitations.length);
    } catch (error) {
      console.error('Erreur chargement invitations:', error);
      setInvitations([]);
      setAcceptedInvites([]);
    }
  };

  // Fonctions utilitaires pour les vues temporelles
  const formatDate = (date) => {
    return new Intl.DateTimeFormat('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date);
  };

  const getWeekDates = (date) => {
    const startOfWeek = new Date(date);
    const day = startOfWeek.getDay();
    const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1); // Lundi comme premier jour
    startOfWeek.setDate(diff);
    
    const weekDates = [];
    for (let i = 0; i < 7; i++) {
      const currentDate = new Date(startOfWeek);
      currentDate.setDate(startOfWeek.getDate() + i);
      weekDates.push(currentDate);
    }
    return weekDates;
  };

  const getMonthDates = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    // Commencer par le lundi de la première semaine
    const startDate = new Date(firstDay);
    const startDay = firstDay.getDay();
    startDate.setDate(firstDay.getDate() - (startDay === 0 ? 6 : startDay - 1));
    
    const monthDates = [];
    const current = new Date(startDate);
    
    while (current <= lastDay || monthDates.length % 7 !== 0) {
      monthDates.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }
    
    return monthDates;
  };

  const navigateDate = (direction) => {
    const newDate = new Date(currentDate);
    if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() + (direction * 7));
    } else if (viewMode === 'month') {
      newDate.setMonth(newDate.getMonth() + direction);
    }
    setCurrentDate(newDate);
  };

  // NEW: Enhanced day detail function
  const openDayDetail = (date) => {
    const daySchedules = getSchedulesForDate(date);
    const dayTeams = teamLeaders.filter(leader => {
      // Logic to check if team leader is assigned to this day
      return daySchedules.some(schedule => schedule.team_leader_id === leader.id);
    });
    
    const dayCollaborators = collaborators.filter(collab => {
      // Logic to check if collaborator is assigned to this day
      return daySchedules.some(schedule => schedule.collaborators?.includes(collab.id));
    });

    setSelectedDayData({
      date: date,
      schedules: daySchedules,
      teams: dayTeams,
      collaborators: dayCollaborators,
      totalHours: daySchedules.reduce((sum, schedule) => sum + (parseInt(schedule.hours) || 0), 0),
      availableSlots: 8 - daySchedules.length // Assuming 8 slots per day
    });
    setDetailedDate(date);
    setSelectedDate(date.toISOString().split('T')[0]);
    setShowDayDetail(true);
  };

  const getSchedulesForDate = (date) => {
    const dateStr = typeof date === 'string' ? date : date.toISOString().split('T')[0];
    return schedules.filter(schedule => schedule.date === dateStr);
  };

  const getDateTitle = () => {
    if (viewMode === 'week') {
      const weekDates = getWeekDates(currentDate);
      const startDate = weekDates[0];
      const endDate = weekDates[6];
      return `Semaine du ${startDate.getDate()}/${startDate.getMonth() + 1} au ${endDate.getDate()}/${endDate.getMonth() + 1}/${endDate.getFullYear()}`;
    } else if (viewMode === 'month') {
      return new Intl.DateTimeFormat('fr-FR', { 
        year: 'numeric', 
        month: 'long' 
      }).format(currentDate);
    }
    return '';
  };

  const addInvitedPersonAsTeamLeader = async (invitation) => {
    const teamLeaderData = {
      nom: invitation.lastName,
      prenom: invitation.firstName,
      email: invitation.email,
      telephone: invitation.phone || '',
      specialite: invitation.skills || 'Généraliste',
      couleur: '#10B981' // Green color for invited persons
    };

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/team-leaders`, teamLeaderData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setTeamLeaders(prev => [...prev, response.data]);
      
      // Mark invitation as used for team leader
      const updatedInvitation = { ...invitation, usedAsTeamLeader: true };
      setAcceptedInvites(prev => prev.map(inv => 
        inv.id === invitation.id ? updatedInvitation : inv
      ));

      alert(`${invitation.firstName} ${invitation.lastName} a été ajouté(e) comme chef d'équipe !`);
    } catch (error) {
      console.error('Erreur ajout chef d\'équipe:', error);
      // Fallback
      const newTeamLeader = {
        id: `invited-${Date.now()}`,
        ...teamLeaderData,
        created_at: new Date().toISOString(),
        fromInvitation: true,
        invitationId: invitation.id
      };

      setTeamLeaders(prev => [...prev, newTeamLeader]);
      
      // Mark invitation as used for team leader
      const updatedInvitation = { ...invitation, usedAsTeamLeader: true };
      setAcceptedInvites(prev => prev.map(inv => 
        inv.id === invitation.id ? updatedInvitation : inv
      ));

      alert(`${invitation.firstName} ${invitation.lastName} a été ajouté(e) comme chef d'équipe !`);
    }
  };

  const addInvitedPersonAsCollaborator = async (invitation) => {
    if (teamLeaders.length === 0) {
      alert('Veuillez d\'abord ajouter un chef d\'équipe avant d\'ajouter des collaborateurs.');
      return;
    }

    const collaboratorData = {
      nom: invitation.lastName,
      prenom: invitation.firstName,
      email: invitation.email,
      telephone: invitation.phone || '',
      competences: invitation.skills || 'Généraliste',
      team_leader_id: teamLeaders[0].id // Assign to first team leader for now
    };

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/collaborators`, collaboratorData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setCollaborators(prev => [...prev, response.data]);
      
      // Mark invitation as used for collaborator
      const updatedInvitation = { ...invitation, usedAsCollaborator: true };
      setAcceptedInvites(prev => prev.map(inv => 
        inv.id === invitation.id ? updatedInvitation : inv
      ));

      alert(`${invitation.firstName} ${invitation.lastName} a été ajouté(e) comme collaborateur !`);
    } catch (error) {
      console.error('Erreur ajout collaborateur:', error);
      // Fallback
      const newCollaborator = {
        id: `invited-collab-${Date.now()}`,
        ...collaboratorData,
        created_at: new Date().toISOString(),
        fromInvitation: true,
        invitationId: invitation.id
      };

      setCollaborators(prev => [...prev, newCollaborator]);
      
      // Mark invitation as used for collaborator
      const updatedInvitation = { ...invitation, usedAsCollaborator: true };
      setAcceptedInvites(prev => prev.map(inv => 
        inv.id === invitation.id ? updatedInvitation : inv
      ));

      alert(`${invitation.firstName} ${invitation.lastName} a été ajouté(e) comme collaborateur !`);
    }
  };

  const addTeamLeader = async () => {
    try {
      if (!teamLeaderData.nom || !teamLeaderData.prenom) {
        alert('Nom et prénom sont obligatoires');
        return;
      }

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/team-leaders`, teamLeaderData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setTeamLeaders(prev => [...prev, response.data]);
      setTeamLeaderData({
        nom: '',
        prenom: '',
        email: '',
        telephone: '',
        specialite: '',
        couleur: '#3B82F6'
      });
      setShowTeamLeaderForm(false);
      alert('Chef d\'équipe ajouté avec succès !');
    } catch (error) {
      console.error('Erreur ajout chef d\'équipe:', error);
      // Fallback en cas d'erreur avec l'API
      const newTeamLeader = {
        id: Date.now().toString(),
        ...teamLeaderData,
        created_at: new Date().toISOString()
      };

      setTeamLeaders(prev => [...prev, newTeamLeader]);
      setTeamLeaderData({
        nom: '',
        prenom: '',
        email: '',
        telephone: '',
        specialite: '',
        couleur: '#3B82F6'
      });
      setShowTeamLeaderForm(false);
      alert('Chef d\'équipe ajouté avec succès !');
    }
  };

  const addCollaborator = async () => {
    try {
      if (!collaboratorData.nom || !collaboratorData.prenom || !collaboratorData.team_leader_id) {
        alert('Nom, prénom et chef d\'équipe sont obligatoires');
        return;
      }

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/collaborators`, collaboratorData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setCollaborators(prev => [...prev, response.data]);
      setCollaboratorData({
        nom: '',
        prenom: '',
        email: '',
        telephone: '',
        competences: '',
        team_leader_id: ''
      });
      setShowCollaboratorForm(false);
      alert('Collaborateur ajouté avec succès !');
    } catch (error) {
      console.error('Erreur ajout collaborateur:', error);
      // Fallback en cas d'erreur avec l'API
      const newCollaborator = {
        id: Date.now().toString(),
        ...collaboratorData,
        created_at: new Date().toISOString()
      };

      setCollaborators(prev => [...prev, newCollaborator]);
      setCollaboratorData({
        nom: '',
        prenom: '',
        email: '',
        telephone: '',
        competences: '',
        team_leader_id: ''
      });
      setShowCollaboratorForm(false);
      alert('Collaborateur ajouté avec succès !');
    }
  };

  const addSchedule = async () => {
    try {
      if (!scheduleData.worksite_id || !scheduleData.team_leader_id || !scheduleData.collaborator_id) {
        alert('Chantier, chef d\'équipe et collaborateur sont obligatoires');
        return;
      }

      const selectedShift = SHIFT_OPTIONS.find(s => s.value === scheduleData.shift);
      
      const scheduleToSend = {
        ...scheduleData,
        hours: selectedShift.hours
      };

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/schedules`, scheduleToSend, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setSchedules(prev => [...prev, response.data]);
      setScheduleData({
        worksite_id: '',
        team_leader_id: '',
        collaborator_id: '',
        date: selectedDate,
        time: '08:00',
        shift: 'day',
        hours: '8',
        description: ''
      });
      setShowScheduleForm(false);
      alert('Planning ajouté avec succès !');
    } catch (error) {
      console.error('Erreur ajout planning:', error);
      // Fallback en cas d'erreur avec l'API
      const selectedShift = SHIFT_OPTIONS.find(s => s.value === scheduleData.shift);
      
      const newSchedule = {
        id: Date.now().toString(),
        ...scheduleData,
        hours: selectedShift.hours,
        status: 'scheduled',
        created_at: new Date().toISOString()
      };

      setSchedules(prev => [...prev, newSchedule]);
      setScheduleData({
        worksite_id: '',
        team_leader_id: '',
        collaborator_id: '',
        date: selectedDate,
        time: '08:00',
        shift: 'day',
        hours: '8',
        description: ''
      });
      setShowScheduleForm(false);
      alert('Planning ajouté avec succès !');
    }
  };

  const removeTeamLeader = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce chef d\'équipe ?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API}/team-leaders/${id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setTeamLeaders(prev => prev.filter(tl => tl.id !== id));
      } catch (error) {
        console.error('Erreur suppression chef d\'équipe:', error);
        // Fallback en cas d'erreur avec l'API
        setTeamLeaders(prev => prev.filter(tl => tl.id !== id));
      }
    }
  };

  const removeCollaborator = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce collaborateur ?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API}/collaborators/${id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setCollaborators(prev => prev.filter(c => c.id !== id));
      } catch (error) {
        console.error('Erreur suppression collaborateur:', error);
        // Fallback en cas d'erreur avec l'API
        setCollaborators(prev => prev.filter(c => c.id !== id));
      }
    }
  };

  const removeSchedule = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce planning ?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API}/schedules/${id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setSchedules(prev => prev.filter(s => s.id !== id));
      } catch (error) {
        console.error('Erreur suppression planning:', error);
        // Fallback en cas d'erreur avec l'API
        setSchedules(prev => prev.filter(s => s.id !== id));
      }
    }
  };

  const getTeamLeaderName = (id) => {
    const leader = teamLeaders.find(tl => tl.id === id);
    return leader ? `${leader.prenom} ${leader.nom}` : 'Inconnu';
  };

  const getCollaboratorName = (id) => {
    const collaborator = collaborators.find(c => c.id === id);
    return collaborator ? `${collaborator.prenom} ${collaborator.nom}` : 'Inconnu';
  };

  const getWorksiteName = (id) => {
    const worksite = worksites.find(w => w.id === id);
    return worksite ? worksite.title : 'Chantier inconnu';
  };

  const getShiftLabel = (shift) => {
    const shiftOption = SHIFT_OPTIONS.find(s => s.value === shift);
    return shiftOption ? shiftOption.label : shift;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement du planning...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-2xl p-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Gestion du Planning</h2>
            <p className="text-gray-600 mt-1">Équipes, collaborateurs et planification des chantiers</p>
          </div>
          <div className="flex space-x-3">
            <Button
              onClick={() => setShowTeamLeaderForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-2xl px-4 py-2"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              + Chef d'équipe
            </Button>
            <Button
              onClick={() => setShowCollaboratorForm(true)}
              className="bg-green-600 hover:bg-green-700 text-white rounded-2xl px-4 py-2"
            >
              <Users className="h-4 w-4 mr-2" />
              + Collaborateur
            </Button>
            <Button
              onClick={() => setShowScheduleForm(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white rounded-2xl px-4 py-2"
            >
              <Calendar className="h-4 w-4 mr-2" />
              + Planning
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="mt-6">
          <div className="flex space-x-1 bg-gray-100 rounded-2xl p-1">
            <button
              onClick={() => setActiveTab('planning')}
              className={`px-6 py-2 rounded-xl font-medium transition-colors ${
                activeTab === 'planning' 
                  ? 'bg-white text-purple-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Calendar className="h-4 w-4 mr-2 inline" />
              Planning ({schedules.length})
            </button>
            <button
              onClick={() => setActiveTab('teams')}
              className={`px-6 py-2 rounded-xl font-medium transition-colors ${
                activeTab === 'teams' 
                  ? 'bg-white text-purple-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Users className="h-4 w-4 mr-2 inline" />
              Équipes ({teamLeaders.length})
            </button>
            <button
              onClick={() => setActiveTab('collaborators')}
              className={`px-6 py-2 rounded-xl font-medium transition-colors ${
                activeTab === 'collaborators' 
                  ? 'bg-white text-purple-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Collaborateurs ({collaborators.length})
            </button>
            <button
              onClick={() => setActiveTab('invitations')}
              className={`px-6 py-2 rounded-xl font-medium transition-colors ${
                activeTab === 'invitations' 
                  ? 'bg-white text-purple-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <UserPlus className="h-4 w-4 mr-2 inline" />
              Personnes Invitées ({invitations.length})
            </button>
          </div>
        </div>
      </div>

      {/* Outils de Visualisation Temporelle - Toujours visible */}
      <Card className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between space-y-4 lg:space-y-0">
            {/* Sélecteur de Vue */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Visualisation du Planning</h3>
              <div className="flex space-x-2">
                <button
                  onClick={() => setViewMode('week')}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-colors ${
                    viewMode === 'week' 
                      ? 'bg-purple-600 text-white shadow-sm' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <CalendarDays className="h-4 w-4" />
                  <span>Semaine</span>
                </button>
                <button
                  onClick={() => setViewMode('month')}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-colors ${
                    viewMode === 'month' 
                      ? 'bg-purple-600 text-white shadow-sm' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <CalendarRange className="h-4 w-4" />
                  <span>Mois</span>
                </button>
              </div>
            </div>

            {/* Navigation Temporelle */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => navigateDate(-1)}
                  className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <div className="px-4 py-2 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-800">{getDateTitle()}</span>
                </div>
                <button
                  onClick={() => navigateDate(1)}
                  className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
              <div className="text-right">
                <button 
                  onClick={() => setCurrentDate(new Date())}
                  className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                >
                  Aujourd'hui
                </button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Planning Content */}
      {activeTab === 'planning' && (
        <div className="space-y-6">

          {/* Vue Calendaire */}
          {viewMode === 'week' && (
            <Card className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg">
              <CardContent className="p-6">
                <div className="grid grid-cols-7 gap-2">
                  {/* En-têtes des jours */}
                  {['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map((day, index) => (
                    <div key={day} className="p-3 text-center font-medium text-gray-600 border-b">
                      {day}
                    </div>
                  ))}
                  
                  {/* Jours de la semaine */}
                  {getWeekDates(currentDate).map((date, index) => {
                    const daySchedules = getSchedulesForDate(date);
                    const isToday = date.toDateString() === new Date().toDateString();
                    const isCurrentMonth = date.getMonth() === currentDate.getMonth();
                    
                    return (
                      <div 
                        key={index} 
                        className={`p-3 min-h-[120px] border border-gray-100 rounded-lg ${
                          isToday ? 'bg-purple-50 border-purple-200' : 
                          isCurrentMonth ? 'bg-white' : 'bg-gray-50'
                        }`}
                      >
                        <div className={`text-center mb-2 ${
                          isToday ? 'font-bold text-purple-600' : 'text-gray-700'
                        }`}>
                          {date.getDate()}
                        </div>
                        <div className="space-y-1">
                          {daySchedules.map((schedule, idx) => (
                            <div key={idx} className="text-xs bg-purple-100 text-purple-700 p-1 rounded truncate">
                              {schedule.time} - {schedule.worksite_name || 'Chantier'}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {viewMode === 'month' && (
            <Card className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg">
              <CardContent className="p-6">
                <div className="grid grid-cols-7 gap-1">
                  {/* En-têtes des jours */}
                  {['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map((day) => (
                    <div key={day} className="p-2 text-center font-medium text-gray-600 border-b">
                      {day}
                    </div>
                  ))}
                  
                  {/* Jours du mois */}
                  {getMonthDates(currentDate).map((date, index) => {
                    const daySchedules = getSchedulesForDate(date);
                    const isToday = date.toDateString() === new Date().toDateString();
                    const isCurrentMonth = date.getMonth() === currentDate.getMonth();
                    
                    return (
                      <div 
                        key={index} 
                        className={`p-2 min-h-[80px] border border-gray-50 ${
                          isToday ? 'bg-purple-50 border-purple-200' : 
                          isCurrentMonth ? 'bg-white hover:bg-purple-50' : 'bg-gray-25 text-gray-400'
                        } cursor-pointer transition-colors hover:shadow-md`}
                        onClick={() => openDayDetail(date)}
                      >
                        <div className={`text-sm mb-1 ${
                          isToday ? 'font-bold text-purple-600' : 
                          isCurrentMonth ? 'text-gray-700' : 'text-gray-400'
                        }`}>
                          {date.getDate()}
                        </div>
                        <div className="space-y-1">
                          {daySchedules.slice(0, 2).map((schedule, idx) => (
                            <div key={idx} className="text-xs bg-purple-100 text-purple-700 p-1 rounded truncate">
                              {schedule.time}
                            </div>
                          ))}
                          {daySchedules.length > 2 && (
                            <div className="text-xs text-gray-500">+{daySchedules.length - 2}</div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Date Selector pour le détail */}
          <Card className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Détail du jour sélectionné</h3>
                  <p className="text-sm text-gray-600">Planning détaillé pour la date sélectionnée</p>
                </div>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
                />
              </div>
            </CardContent>
          </Card>

          {/* Schedules for Selected Date */}
          <div className="grid gap-4">
            {getSchedulesForDate(selectedDate).length === 0 ? (
              <Card className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg">
                <CardContent className="p-12 text-center">
                  <Calendar className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun planning</h3>
                  <p className="text-gray-500">Aucune intervention programmée pour cette date.</p>
                </CardContent>
              </Card>
            ) : (
              getSchedulesForDate(selectedDate).map((schedule) => (
                <Card key={schedule.id} className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {getWorksiteName(schedule.worksite_id)}
                        </h3>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <div>
                            <span className="text-sm font-medium text-gray-700">Chef d'équipe:</span>
                            <p className="text-gray-900">{getTeamLeaderName(schedule.team_leader_id)}</p>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-700">Collaborateur:</span>
                            <p className="text-gray-900">{getCollaboratorName(schedule.collaborator_id)}</p>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-700">Horaire:</span>
                            <p className="text-gray-900">{getShiftLabel(schedule.shift)} - {schedule.hours}h</p>
                            {schedule.time && (
                              <p className="text-sm text-gray-600">Début: {schedule.time}</p>
                            )}
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-700">Statut:</span>
                            <Badge className={`ml-2 ${
                              schedule.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                              schedule.status === 'in_progress' ? 'bg-orange-100 text-orange-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {schedule.status}
                            </Badge>
                          </div>
                        </div>
                        
                        {schedule.description && (
                          <div className="bg-gray-50 rounded-xl p-3">
                            <p className="text-sm text-gray-700">
                              <strong>Description:</strong> {schedule.description}
                            </p>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" className="rounded-xl">
                          <Edit className="h-4 w-4 mr-1" />
                          Modifier
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => removeSchedule(schedule.id)}
                          className="rounded-xl border-red-200 text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Supprimer
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      )}

      {/* Team Leaders Tab */}
      {activeTab === 'teams' && (
        <div className="grid gap-4">
          {teamLeaders.length === 0 ? (
            <Card className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg">
              <CardContent className="p-12 text-center">
                <UserPlus className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun chef d'équipe</h3>
                <p className="text-gray-500">Ajoutez votre premier chef d'équipe pour commencer.</p>
              </CardContent>
            </Card>
          ) : (
            teamLeaders.map((leader) => (
              <Card key={leader.id} className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <div 
                        className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold"
                        style={{ backgroundColor: leader.couleur }}
                      >
                        {leader.prenom.charAt(0)}{leader.nom.charAt(0)}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">{leader.prenom} {leader.nom}</h3>
                        <p className="text-gray-600">{leader.specialite}</p>
                        <div className="mt-2 space-y-1 text-sm text-gray-500">
                          <p>📧 {leader.email}</p>
                          <p>📱 {leader.telephone}</p>
                          <p>🏷️ Couleur: <span className="inline-block w-4 h-4 rounded ml-1" style={{ backgroundColor: leader.couleur }}></span></p>
                        </div>
                        <p className="text-xs text-gray-400 mt-2">Ajouté le {new Date(leader.created_at).toLocaleDateString('fr-FR')}</p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline" className="rounded-xl">
                        <Edit className="h-4 w-4 mr-1" />
                        Modifier
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => removeTeamLeader(leader.id)}
                        className="rounded-xl border-red-200 text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4 mr-1" />
                        Supprimer
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Collaborators Tab */}
      {activeTab === 'collaborators' && (
        <div className="grid gap-4">
          {collaborators.length === 0 ? (
            <Card className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg">
              <CardContent className="p-12 text-center">
                <Users className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun collaborateur</h3>
                <p className="text-gray-500">Ajoutez votre premier collaborateur pour commencer.</p>
              </CardContent>
            </Card>
          ) : (
            collaborators.map((collaborator) => {
              const teamLeader = teamLeaders.find(tl => tl.id === collaborator.team_leader_id);
              return (
                <Card key={collaborator.id} className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4">
                        <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center">
                          <Users className="h-6 w-6 text-gray-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">{collaborator.prenom} {collaborator.nom}</h3>
                          <p className="text-gray-600">Sous la direction de: {teamLeader ? `${teamLeader.prenom} ${teamLeader.nom}` : 'Chef non assigné'}</p>
                          <div className="mt-2 space-y-1 text-sm text-gray-500">
                            <p>📧 {collaborator.email}</p>
                            <p>📱 {collaborator.telephone}</p>
                            <p>🛠️ {collaborator.competences}</p>
                          </div>
                          <p className="text-xs text-gray-400 mt-2">Ajouté le {new Date(collaborator.created_at).toLocaleDateString('fr-FR')}</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" className="rounded-xl">
                          <Edit className="h-4 w-4 mr-1" />
                          Modifier
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => removeCollaborator(collaborator.id)}
                          className="rounded-xl border-red-200 text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Supprimer
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      )}

      {/* Invitations Tab */}
      {activeTab === 'invitations' && (
        <div className="grid gap-4">
          {acceptedInvites.length === 0 ? (
            <Card className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg">
              <CardContent className="p-12 text-center">
                <UserPlus className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucune personne invitée</h3>
                <p className="text-gray-500">Les personnes qui ont accepté vos invitations apparaîtront ici et pourront être assignées aux équipes.</p>
              </CardContent>
            </Card>
          ) : (
            acceptedInvites.map((invitation) => (
              <Card key={invitation.id} className="bg-white/80 backdrop-blur-xl rounded-3xl border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-blue-100 rounded-xl flex items-center justify-center">
                        <UserPlus className="h-6 w-6 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {invitation.firstName} {invitation.lastName}
                        </h3>
                        <p className="text-gray-600">Rôle: {invitation.role}</p>
                        <div className="mt-2 space-y-1 text-sm text-gray-500">
                          <p>📧 {invitation.email}</p>
                          {invitation.phone && <p>📱 {invitation.phone}</p>}
                          <p>🛠️ Compétences: {invitation.skills || 'Généraliste'}</p>
                          <p>✅ Accepté le: {new Date(invitation.accepted_at || invitation.createdAt).toLocaleDateString('fr-FR')}</p>
                        </div>
                        <div className="mt-3 flex space-x-2">
                          {invitation.usedAsTeamLeader && (
                            <Badge className="bg-purple-100 text-purple-700">
                              👑 Chef d'équipe assigné
                            </Badge>
                          )}
                          {invitation.usedAsCollaborator && (
                            <Badge className="bg-blue-100 text-blue-700">
                              🤝 Collaborateur assigné
                            </Badge>
                          )}
                          {!invitation.usedAsTeamLeader && !invitation.usedAsCollaborator && (
                            <Badge className="bg-green-100 text-green-700">
                              ✅ Disponible pour assignation
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col space-y-2">
                      {!invitation.usedAsTeamLeader && (
                        <Button 
                          size="sm"
                          onClick={() => addInvitedPersonAsTeamLeader(invitation)}
                          className="bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs px-3 py-2"
                        >
                          👑 Chef d'équipe
                        </Button>
                      )}
                      {!invitation.usedAsCollaborator && (
                        <Button 
                          size="sm"
                          onClick={() => addInvitedPersonAsCollaborator(invitation)}
                          className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs px-3 py-2"
                        >
                          🤝 Collaborateur
                        </Button>
                      )}
                      {(invitation.usedAsTeamLeader || invitation.usedAsCollaborator) && (
                        <div className="text-center">
                          <p className="text-xs text-green-600 font-medium">✅ Assigné</p>
                          <p className="text-xs text-gray-500">Déjà dans l'équipe</p>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Modals for Forms */}
      
      {/* Team Leader Form Modal */}
      {showTeamLeaderForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="bg-white rounded-3xl shadow-2xl max-w-md w-full mx-4">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl font-semibold text-gray-900">Nouveau Chef d'équipe</CardTitle>
                <Button
                  onClick={() => setShowTeamLeaderForm(false)}
                  variant="ghost"
                  size="sm"
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  placeholder="Prénom *"
                  value={teamLeaderData.prenom}
                  onChange={(e) => setTeamLeaderData(prev => ({...prev, prenom: e.target.value}))}
                  className="rounded-xl border-gray-200"
                />
                <Input
                  placeholder="Nom *"
                  value={teamLeaderData.nom}
                  onChange={(e) => setTeamLeaderData(prev => ({...prev, nom: e.target.value}))}
                  className="rounded-xl border-gray-200"
                />
              </div>
              
              <Input
                type="email"
                placeholder="Email"
                value={teamLeaderData.email}
                onChange={(e) => setTeamLeaderData(prev => ({...prev, email: e.target.value}))}
                className="rounded-xl border-gray-200"
              />
              
              <Input
                placeholder="Téléphone"
                value={teamLeaderData.telephone}
                onChange={(e) => setTeamLeaderData(prev => ({...prev, telephone: e.target.value}))}
                className="rounded-xl border-gray-200"
              />
              
              <select
                value={teamLeaderData.specialite}
                onChange={(e) => setTeamLeaderData(prev => ({...prev, specialite: e.target.value}))}
                className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
              >
                <option value="">Sélectionnez une spécialité</option>
                {SPECIALTIES.map(specialty => (
                  <option key={specialty} value={specialty}>{specialty}</option>
                ))}
              </select>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Couleur d'identification</label>
                <div className="flex space-x-2">
                  {COLORS.map(color => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => setTeamLeaderData(prev => ({...prev, couleur: color}))}
                      className={`w-8 h-8 rounded-lg border-2 ${
                        teamLeaderData.couleur === color ? 'border-gray-900' : 'border-gray-200'
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <Button variant="outline" onClick={() => setShowTeamLeaderForm(false)} className="flex-1">
                  Annuler
                </Button>
                <Button onClick={addTeamLeader} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white">
                  Ajouter Chef
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Collaborator Form Modal */}
      {showCollaboratorForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="bg-white rounded-3xl shadow-2xl max-w-md w-full mx-4">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl font-semibold text-gray-900">Nouveau Collaborateur</CardTitle>
                <Button
                  onClick={() => setShowCollaboratorForm(false)}
                  variant="ghost"
                  size="sm"
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  placeholder="Prénom *"
                  value={collaboratorData.prenom}
                  onChange={(e) => setCollaboratorData(prev => ({...prev, prenom: e.target.value}))}
                  className="rounded-xl border-gray-200"
                />
                <Input
                  placeholder="Nom *"
                  value={collaboratorData.nom}
                  onChange={(e) => setCollaboratorData(prev => ({...prev, nom: e.target.value}))}
                  className="rounded-xl border-gray-200"
                />
              </div>
              
              <select
                value={collaboratorData.team_leader_id}
                onChange={(e) => setCollaboratorData(prev => ({...prev, team_leader_id: e.target.value}))}
                className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
              >
                <option value="">Sélectionnez un chef d'équipe *</option>
                {teamLeaders.map(leader => (
                  <option key={leader.id} value={leader.id}>
                    {leader.prenom} {leader.nom} - {leader.specialite}
                  </option>
                ))}
              </select>
              
              <Input
                type="email"
                placeholder="Email"
                value={collaboratorData.email}
                onChange={(e) => setCollaboratorData(prev => ({...prev, email: e.target.value}))}
                className="rounded-xl border-gray-200"
              />
              
              <Input
                placeholder="Téléphone"
                value={collaboratorData.telephone}
                onChange={(e) => setCollaboratorData(prev => ({...prev, telephone: e.target.value}))}
                className="rounded-xl border-gray-200"
              />
              
              <textarea
                placeholder="Compétences et qualifications"
                value={collaboratorData.competences}
                onChange={(e) => setCollaboratorData(prev => ({...prev, competences: e.target.value}))}
                rows={3}
                className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3 resize-none"
              />
              
              <div className="flex space-x-3 pt-4">
                <Button variant="outline" onClick={() => setShowCollaboratorForm(false)} className="flex-1">
                  Annuler
                </Button>
                <Button onClick={addCollaborator} className="flex-1 bg-green-600 hover:bg-green-700 text-white">
                  Ajouter Collaborateur
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Schedule Form Modal */}
      {showScheduleForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="bg-white rounded-3xl shadow-2xl max-w-lg w-full mx-4">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl font-semibold text-gray-900">Nouveau Planning</CardTitle>
                <Button
                  onClick={() => setShowScheduleForm(false)}
                  variant="ghost"
                  size="sm"
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <select
                value={scheduleData.worksite_id}
                onChange={(e) => setScheduleData(prev => ({...prev, worksite_id: e.target.value}))}
                className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
              >
                <option value="">Sélectionnez un chantier *</option>
                {worksites.map(worksite => (
                  <option key={worksite.id} value={worksite.id}>
                    {worksite.title}
                  </option>
                ))}
              </select>
              
              <div className="grid grid-cols-2 gap-4">
                <select
                  value={scheduleData.team_leader_id}
                  onChange={(e) => setScheduleData(prev => ({...prev, team_leader_id: e.target.value}))}
                  className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
                >
                  <option value="">Chef d'équipe *</option>
                  {teamLeaders.map(leader => (
                    <option key={leader.id} value={leader.id}>
                      {leader.prenom} {leader.nom}
                    </option>
                  ))}
                </select>
                
                <select
                  value={scheduleData.collaborator_id}
                  onChange={(e) => setScheduleData(prev => ({...prev, collaborator_id: e.target.value}))}
                  className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
                >
                  <option value="">Collaborateur *</option>
                  {collaborators
                    .filter(collab => !scheduleData.team_leader_id || collab.team_leader_id === scheduleData.team_leader_id)
                    .map(collaborator => (
                    <option key={collaborator.id} value={collaborator.id}>
                      {collaborator.prenom} {collaborator.nom}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date de l'intervention</label>
                  <input
                    type="date"
                    value={scheduleData.date}
                    onChange={(e) => setScheduleData(prev => ({...prev, date: e.target.value}))}
                    className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Heure de début</label>
                  <input
                    type="time"
                    value={scheduleData.time}
                    onChange={(e) => setScheduleData(prev => ({...prev, time: e.target.value}))}
                    className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type d'intervention</label>
                  <select
                    value={scheduleData.shift}
                    onChange={(e) => setScheduleData(prev => ({...prev, shift: e.target.value}))}
                    className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3"
                  >
                    {SHIFT_OPTIONS.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description de l'intervention (optionnel)</label>
                <textarea
                  placeholder="Détails sur l'intervention prévue..."
                  value={scheduleData.description}
                  onChange={(e) => setScheduleData(prev => ({...prev, description: e.target.value}))}
                  rows={3}
                  className="w-full rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 p-3 resize-none"
                />
              </div>
              
              <div className="bg-purple-50 rounded-xl p-4">
                <h4 className="font-medium text-purple-900 mb-2">Résumé du planning :</h4>
                <p className="text-sm text-purple-700">
                  <strong>Duo :</strong> {getTeamLeaderName(scheduleData.team_leader_id)} + {getCollaboratorName(scheduleData.collaborator_id)}
                  <br />
                  <strong>Horaire :</strong> {getShiftLabel(scheduleData.shift)}
                  <br />
                  <strong>Date :</strong> {scheduleData.date ? new Date(scheduleData.date).toLocaleDateString('fr-FR') : 'Non définie'}
                </p>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <Button variant="outline" onClick={() => setShowScheduleForm(false)} className="flex-1">
                  Annuler
                </Button>
                <Button onClick={addSchedule} className="flex-1 bg-purple-600 hover:bg-purple-700 text-white">
                  Créer Planning
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* NEW: Day Detail Modal */}
      {showDayDetail && selectedDayData && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-8">
              {/* Header */}
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Planning du {selectedDayData.date.toLocaleDateString('fr-FR', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </h2>
                  <p className="text-gray-600 mt-1">
                    Détail complet de la journée • {selectedDayData.totalHours}h programmées • {selectedDayData.availableSlots} créneaux libres
                  </p>
                </div>
                <Button
                  onClick={() => setShowDayDetail(false)}
                  variant="outline"
                  className="rounded-xl px-4 py-2"
                >
                  <X className="h-4 w-4 mr-2" />
                  Fermer
                </Button>
              </div>

              {/* Day Statistics */}
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 rounded-2xl p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">{selectedDayData.schedules.length}</div>
                  <div className="text-sm text-blue-700">Interventions</div>
                </div>
                <div className="bg-purple-50 rounded-2xl p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">{selectedDayData.teams.length}</div>
                  <div className="text-sm text-purple-700">Équipes</div>
                </div>
                <div className="bg-green-50 rounded-2xl p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">{selectedDayData.collaborators.length}</div>
                  <div className="text-sm text-green-700">Collaborateurs</div>
                </div>
                <div className="bg-orange-50 rounded-2xl p-4 text-center">
                  <div className="text-2xl font-bold text-orange-600">{selectedDayData.totalHours}h</div>
                  <div className="text-sm text-orange-700">Total Heures</div>
                </div>
              </div>

              {/* Interventions Details */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Interventions Programmées</h3>
                  {selectedDayData.schedules.length === 0 ? (
                    <div className="bg-gray-50 rounded-2xl p-8 text-center">
                      <Calendar className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                      <p className="text-gray-600">Aucune intervention programmée pour cette journée</p>
                      <Button
                        onClick={() => {
                          setShowDayDetail(false);
                          setShowScheduleForm(true);
                        }}
                        className="mt-4 bg-purple-600 hover:bg-purple-700 text-white rounded-xl px-6 py-2"
                      >
                        <Calendar className="h-4 w-4 mr-2" />
                        Programmer une intervention
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {selectedDayData.schedules.map((schedule, index) => (
                        <div key={schedule.id || index} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-all duration-200">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-3">
                                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                                <h4 className="text-lg font-semibold text-gray-900">{schedule.title || 'Intervention'}</h4>
                                <span className="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full">
                                  {schedule.time}
                                </span>
                              </div>
                              
                              <div className="grid md:grid-cols-2 gap-4 mb-4">
                                <div>
                                  <p className="text-sm text-gray-600 mb-1"><strong>Durée:</strong> {schedule.hours}h</p>
                                  <p className="text-sm text-gray-600 mb-1"><strong>Période:</strong> {schedule.period}</p>
                                  <p className="text-sm text-gray-600"><strong>Date:</strong> {new Date(schedule.date).toLocaleDateString('fr-FR')}</p>
                                </div>
                                <div>
                                  <p className="text-sm text-gray-600 mb-1"><strong>Équipe assignée:</strong> {schedule.team_id ? 'Équipe #' + schedule.team_id : 'Non assignée'}</p>
                                  <p className="text-sm text-gray-600"><strong>Statut:</strong> <span className="text-green-600">Planifiée</span></p>
                                </div>
                              </div>
                              
                              {schedule.description && (
                                <div className="bg-blue-50 rounded-lg p-3 mb-3">
                                  <p className="text-sm text-blue-800"><strong>Description:</strong> {schedule.description}</p>
                                </div>
                              )}
                            </div>
                            
                            <div className="flex space-x-2 ml-4">
                              <Button size="sm" variant="outline" className="rounded-lg text-xs">
                                <Edit className="h-3 w-3 mr-1" />
                                Modifier
                              </Button>
                              <Button size="sm" variant="outline" className="rounded-lg text-xs border-red-200 text-red-600 hover:bg-red-50">
                                <Trash2 className="h-3 w-3 mr-1" />
                                Supprimer
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Team Assignment Section */}
                {selectedDayData.teams.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Équipes Assignées</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {selectedDayData.teams.map((team, index) => (
                        <div key={team.id || index} className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-4">
                          <div className="flex items-center space-x-3">
                            <div 
                              className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold"
                              style={{ backgroundColor: team.couleur }}
                            >
                              {team.prenom.charAt(0)}{team.nom.charAt(0)}
                            </div>
                            <div>
                              <h4 className="font-semibold text-gray-900">{team.prenom} {team.nom}</h4>
                              <p className="text-sm text-gray-600">{team.specialite}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quick Actions */}
                <div className="bg-gray-50 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions Rapides</h3>
                  <div className="flex flex-wrap gap-3">
                    <Button
                      onClick={() => {
                        setShowDayDetail(false);
                        setShowScheduleForm(true);
                      }}
                      className="bg-purple-600 hover:bg-purple-700 text-white rounded-xl"
                    >
                      <Calendar className="h-4 w-4 mr-2" />
                      Nouvelle Intervention
                    </Button>
                    <Button
                      onClick={() => {
                        setShowDayDetail(false);
                        setShowTeamLeaderForm(true);
                      }}
                      variant="outline"
                      className="rounded-xl"
                    >
                      <UserPlus className="h-4 w-4 mr-2" />
                      Assigner Équipe
                    </Button>
                    <Button variant="outline" className="rounded-xl">
                      <Clock className="h-4 w-4 mr-2" />
                      Gestion Horaires
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlanningManagement;