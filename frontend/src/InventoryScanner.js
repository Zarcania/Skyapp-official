import React, { useState, useEffect, useRef } from 'react';
import { Camera, Package, ScanLine, X, CheckCircle, Clock, AlertTriangle, Calendar } from 'lucide-react';
import { api } from './lib/supabase';

const InventoryScanner = () => {
  const [myCheckouts, setMyCheckouts] = useState([]);
  const [availableMaterials, setAvailableMaterials] = useState([]);
  const [history, setHistory] = useState([]);
  const [activeView, setActiveView] = useState('my-items'); // 'my-items', 'scan', 'available', 'history'
  const [loading, setLoading] = useState(false);
  const [scanMode, setScanMode] = useState(false);
  const [qrResult, setQrResult] = useState(null);
  const [checkoutNotes, setCheckoutNotes] = useState('');
  const [expectedReturn, setExpectedReturn] = useState('');
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    loadMyCheckouts();
  }, []);

  const loadMyCheckouts = async () => {
    setLoading(true);
    try {
      const data = await api.inventory.getMyCheckouts();
      setMyCheckouts(data);
    } catch (error) {
      console.error('Erreur chargement emprunts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableMaterials = async () => {
    setLoading(true);
    try {
      const data = await api.inventory.getAvailable();
      setAvailableMaterials(data);
    } catch (error) {
      console.error('Erreur chargement matériel disponible:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await api.inventory.getHistory();
      setHistory(data);
    } catch (error) {
      console.error('Erreur chargement historique:', error);
    } finally {
      setLoading(false);
    }
  };

  const startScanner = async () => {
    setScanMode(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }
    } catch (error) {
      alert('Impossible d\'accéder à la caméra: ' + error.message);
      setScanMode(false);
    }
  };

  const stopScanner = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setScanMode(false);
    setQrResult(null);
  };

  const handleManualQR = async (qrCode) => {
    try {
      setLoading(true);
      const data = await api.inventory.checkout({
        qr_code: qrCode,
        notes: checkoutNotes,
        expected_return_date: expectedReturn || null
      });
      alert('✅ Matériel emprunté avec succès !');
      setQrResult(null);
      setCheckoutNotes('');
      setExpectedReturn('');
      stopScanner();
      loadMyCheckouts();
    } catch (error) {
      alert('❌ Erreur: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (checkoutId) => {
    if (!confirm('Confirmer le retour de ce matériel ?')) return;
    
    const notes = prompt('Notes de retour (optionnel):');
    try {
      setLoading(true);
      await api.inventory.checkin(checkoutId, { notes });
      alert('✅ Matériel retourné avec succès !');
      loadMyCheckouts();
    } catch (error) {
      alert('❌ Erreur: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getDaysRemaining = (expectedReturn) => {
    if (!expectedReturn) return null;
    const diff = new Date(expectedReturn) - new Date();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return days;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Package className="text-blue-600" />
          Mon Inventaire
        </h1>
        <p className="text-gray-600 mt-1">Gérez vos emprunts de matériel</p>
      </div>

      {/* Navigation */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        <button
          onClick={() => { setActiveView('my-items'); loadMyCheckouts(); }}
          className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap ${
            activeView === 'my-items'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Mes emprunts ({myCheckouts.length})
        </button>
        <button
          onClick={() => { setActiveView('scan'); }}
          className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap flex items-center gap-2 ${
            activeView === 'scan'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <ScanLine size={18} />
          Scanner QR
        </button>
        <button
          onClick={() => { setActiveView('available'); loadAvailableMaterials(); }}
          className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap ${
            activeView === 'available'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Disponible
        </button>
        <button
          onClick={() => { setActiveView('history'); loadHistory(); }}
          className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap ${
            activeView === 'history'
              ? 'bg-gray-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Historique
        </button>
      </div>

      {/* Mes emprunts */}
      {activeView === 'my-items' && (
        <div>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
            </div>
          ) : myCheckouts.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Vous n'avez aucun matériel emprunté</p>
              <button
                onClick={() => setActiveView('scan')}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Scanner un QR code
              </button>
            </div>
          ) : (
            <div className="grid gap-4">
              {myCheckouts.map((checkout) => {
                const daysLeft = getDaysRemaining(checkout.expected_return_date);
                const isOverdue = daysLeft !== null && daysLeft < 0;
                const isWarning = daysLeft !== null && daysLeft <= 3 && daysLeft >= 0;

                return (
                  <div key={checkout.id} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900">
                          {checkout.materials?.name || 'Matériel'}
                        </h3>
                        <p className="text-sm text-gray-600">{checkout.materials?.category}</p>
                        <div className="mt-3 space-y-1 text-sm">
                          <div className="flex items-center gap-2 text-gray-700">
                            <Clock size={16} />
                            Emprunté le {formatDate(checkout.checked_out_at)}
                          </div>
                          {checkout.expected_return_date && (
                            <div className={`flex items-center gap-2 ${
                              isOverdue ? 'text-red-600 font-medium' :
                              isWarning ? 'text-orange-600 font-medium' :
                              'text-gray-700'
                            }`}>
                              <Calendar size={16} />
                              Retour prévu: {formatDate(checkout.expected_return_date)}
                              {daysLeft !== null && (
                                <span className="ml-2">
                                  ({daysLeft > 0 ? `${daysLeft}j restants` : `${Math.abs(daysLeft)}j de retard`})
                                </span>
                              )}
                            </div>
                          )}
                          {checkout.checkout_notes && (
                            <p className="text-gray-600 italic">Note: {checkout.checkout_notes}</p>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => handleReturn(checkout.id)}
                        disabled={loading}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                      >
                        <CheckCircle size={18} />
                        Retourner
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Scanner QR */}
      {activeView === 'scan' && (
        <div className="bg-white rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Scanner un QR Code</h2>
          
          {!scanMode ? (
            <div className="text-center py-12">
              <Camera className="w-20 h-20 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-6">Scannez le QR code sur le matériel pour l'emprunter</p>
              <button
                onClick={startScanner}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 mx-auto"
              >
                <Camera size={20} />
                Activer la caméra
              </button>
              
              <div className="mt-8 pt-8 border-t">
                <p className="text-sm text-gray-600 mb-3">Ou entrez le code QR manuellement:</p>
                <input
                  type="text"
                  placeholder="QR-XXXXX"
                  className="px-4 py-2 border rounded-lg w-64"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && e.target.value) {
                      handleManualQR(e.target.value);
                    }
                  }}
                />
              </div>
            </div>
          ) : (
            <div>
              <div className="relative bg-black rounded-lg overflow-hidden mb-4">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full"
                  style={{ maxHeight: '400px' }}
                />
                <button
                  onClick={stopScanner}
                  className="absolute top-4 right-4 p-2 bg-red-600 text-white rounded-full hover:bg-red-700"
                >
                  <X size={20} />
                </button>
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-64 h-64 border-4 border-blue-500 rounded-lg"></div>
                </div>
              </div>
              
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Notes (optionnel)"
                  value={checkoutNotes}
                  onChange={(e) => setCheckoutNotes(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                />
                <input
                  type="date"
                  placeholder="Date de retour prévue"
                  value={expectedReturn}
                  onChange={(e) => setExpectedReturn(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>
              
              <p className="text-sm text-gray-600 mt-4 text-center">
                📱 Positionnez le QR code dans le cadre bleu
              </p>
            </div>
          )}
        </div>
      )}

      {/* Matériel disponible */}
      {activeView === 'available' && (
        <div>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableMaterials.map((material) => (
                <div key={material.id} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <h3 className="font-semibold text-gray-900">{material.name}</h3>
                  <p className="text-sm text-gray-600">{material.category}</p>
                  <p className="text-xs text-gray-500 mt-2">{material.serial_number}</p>
                  <span className="inline-block mt-3 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                    ✓ Disponible
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Historique */}
      {activeView === 'history' && (
        <div>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-gray-600 border-t-transparent rounded-full mx-auto"></div>
            </div>
          ) : (
            <div className="space-y-2">
              {history.map((checkout) => (
                <div key={checkout.id} className="bg-white border rounded-lg p-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-medium text-gray-900">{checkout.materials?.name}</h4>
                    <p className="text-sm text-gray-600">
                      {formatDate(checkout.checked_out_at)} → {
                        checkout.checked_in_at ? formatDate(checkout.checked_in_at) : 'En cours'
                      }
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    checkout.status === 'returned' ? 'bg-gray-100 text-gray-700' :
                    checkout.status === 'overdue' ? 'bg-red-100 text-red-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {checkout.status === 'returned' ? 'Retourné' :
                     checkout.status === 'overdue' ? 'En retard' : 'Actif'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InventoryScanner;
