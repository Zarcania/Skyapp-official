import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

// Mock axios as ESM-friendly factory to avoid parsing the real module
jest.mock('axios', () => {
  const m = { post: jest.fn(), patch: jest.fn() };
  return { __esModule: true, default: m, ...m };
});

// Mock react-router-dom to avoid full routing ESM issues in test environment
jest.mock('react-router-dom', () => {
  return {
    __esModule: true,
    BrowserRouter: ({ children }) => <div>{children}</div>,
    Routes: ({ children }) => <div>{children}</div>,
    Route: () => null,
    Navigate: () => null,
    useNavigate: () => jest.fn()
  };
}, { virtual: true });

// Require App AFTER mocks are set so axios is mocked for its imports
const { SearchForm, AuthContext } = require('../App');
const axios = require('axios').default;

const renderWithAuth = (ui) => {
  return render(
    <AuthContext.Provider value={{ token: 'fake-token', user: { id: 'user-1' } }}>
      {ui}
    </AuthContext.Provider>
  );
};

// Utility: advance timers after debounce
const advanceDebounce = async () => {
  jest.advanceTimersByTime(1600);
  // allow promises to flush
  await Promise.resolve();
};

describe('SearchForm draft autosave', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  axios.post.mockResolvedValue({ data: { search: { id: 'draft-123', created_at: new Date().toISOString() } } });
  axios.patch.mockResolvedValue({ data: { message: 'ok' } });
    localStorage.setItem('token', 'fake-token');
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.useRealTimers();
    jest.resetAllMocks();
    localStorage.clear();
  });

  it('crée un brouillon et effectue une sauvegarde après modification', async () => {
    jest.setTimeout(20000);
    const user = userEvent.setup({ advanceTimers: (ms) => jest.advanceTimersByTime(ms) });
    const draftEvents = [];
  renderWithAuth(<SearchForm onDraftEvent={(e) => draftEvents.push(e)} />);

  // Trouver un champ texte et cibler l'adresse (3e champ de la section générale)
  const textboxes = screen.getAllByRole('textbox');
  const adresseInput = textboxes[2];
  await user.clear(adresseInput);
  await user.type(adresseInput, '12 Rue de Test');

    // Déclenche le délai de debounce
  await advanceDebounce();
  // laisser le patch async se résoudre
  await Promise.resolve();
  await Promise.resolve();

    // Vérifier appels réseau
  expect(axios.post).toHaveBeenCalledTimes(1); // création brouillon
  expect(axios.patch.mock.calls.length).toBeGreaterThanOrEqual(1); // au moins une autosave

    // Vérifier qu'un event saved est passé
    expect(draftEvents.find(e => e.type === 'saved')).toBeTruthy();

    // Indicateur visuel doit afficher "Sauvegardé"
    const savedIndicator = await screen.findByText(/Sauvegardé/i);
    expect(savedIndicator).toBeInTheDocument();
  });
});
