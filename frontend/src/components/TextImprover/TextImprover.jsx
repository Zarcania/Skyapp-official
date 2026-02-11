import React, { useState } from 'react';
import axios from 'axios';
import './TextImprover.css';

const API = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8001/api';

/**
 * ✨ Composant de correction orthographique et amélioration de texte
 * Optimisé pour les rapports techniciens BTP
 */
const TextImprover = ({ initialText = '', onTextImproved, placeholder = "Saisissez votre rapport..." }) => {
  const [text, setText] = useState(initialText);
  const [improvedText, setImprovedText] = useState('');
  const [isImproving, setIsImproving] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [stats, setStats] = useState(null);

  const handleImproveText = async () => {
    if (!text.trim()) {
      alert('⚠️ Veuillez saisir du texte à améliorer');
      return;
    }

    setIsImproving(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/ai/improve-text`,
        null,
        {
          params: { text: text },
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        setImprovedText(response.data.improved);
        setStats({
          tokens: response.data.tokens,
          cost: response.data.cost_euros
        });
        setShowComparison(true);
      } else {
        alert(`❌ ${response.data.message || 'Erreur lors de l\'amélioration'}`);
      }
    } catch (error) {
      console.error('Erreur amélioration texte:', error);
      alert('❌ Erreur lors de l\'amélioration du texte. Vérifiez votre connexion.');
    } finally {
      setIsImproving(false);
    }
  };

  const handleAcceptImproved = () => {
    setText(improvedText);
    if (onTextImproved) {
      onTextImproved(improvedText);
    }
    setShowComparison(false);
    setImprovedText('');
  };

  const handleReject = () => {
    setShowComparison(false);
    setImprovedText('');
  };

  return (
    <div className="text-improver">
      {!showComparison ? (
        // Mode édition normale
        <div className="text-improver-editor">
          <div className="text-improver-header">
            <label className="text-improver-label">
              📝 Rapport / Commentaire
            </label>
            <button
              type="button"
              className="improve-btn"
              onClick={handleImproveText}
              disabled={isImproving || !text.trim()}
              title="✨ Corriger l'orthographe et améliorer le texte"
            >
              {isImproving ? (
                <>
                  <svg className="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"></circle>
                  </svg>
                  Amélioration...
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2l2 7h7l-5.5 4.5 2 7L12 16l-5.5 4.5 2-7L3 9h7z"></path>
                  </svg>
                  ✨ Améliorer avec IA
                </>
              )}
            </button>
          </div>

          <textarea
            className="text-improver-textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={placeholder}
            rows={8}
            disabled={isImproving}
          />

          <div className="text-improver-hint">
            💡 Astuce : Rédigez librement, l'IA corrigera automatiquement l'orthographe et rendra le texte plus professionnel
          </div>
        </div>
      ) : (
        // Mode comparaison
        <div className="text-improver-comparison">
          <div className="comparison-header">
            <h3>✨ Texte amélioré par l'IA</h3>
            {stats && (
              <div className="comparison-stats">
                <span>{stats.tokens} tokens</span>
                <span>≈ {stats.cost.toFixed(4)}€</span>
              </div>
            )}
          </div>

          <div className="comparison-grid">
            <div className="comparison-col">
              <div className="comparison-label">📝 Texte original</div>
              <div className="comparison-text original">
                {text}
              </div>
            </div>

            <div className="comparison-arrow">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </div>

            <div className="comparison-col">
              <div className="comparison-label">✨ Texte amélioré</div>
              <div className="comparison-text improved">
                {improvedText}
              </div>
            </div>
          </div>

          <div className="comparison-actions">
            <button
              type="button"
              className="btn-reject"
              onClick={handleReject}
            >
              ❌ Refuser
            </button>
            <button
              type="button"
              className="btn-accept"
              onClick={handleAcceptImproved}
            >
              ✅ Accepter
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TextImprover;
