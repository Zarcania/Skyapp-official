// =====================================================
// COMPOSANTS FRONTEND: Réception, E-Reporting, Archivage
// À intégrer dans App.js
// =====================================================

// =====================================================
// 1. MODULE RÉCEPTION FACTURES
// =====================================================

const ReceivedInvoicesModule = () => {
  const [receivedInvoices, setReceivedInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadData, setUploadData] = useState({
    file: null,
    supplier_name: '',
    supplier_siren: '',
    invoice_number: '',
    invoice_date: new Date().toISOString().split('T')[0],
    due_date: '',
    total_ht: '',
    total_tva: '',
    total_ttc: '',
    format_type: 'pdf-simple',
    notes: ''
  });

  useEffect(() => {
    loadReceivedInvoices();
  }, []);

  const loadReceivedInvoices = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/invoices/received`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setReceivedInvoices(response.data || []);
    } catch (error) {
      console.error('Erreur chargement factures reçues:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadData({ ...uploadData, file });
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!uploadData.file) {
      alert('Veuillez sélectionner un fichier');
      return;
    }

    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', uploadData.file);
      formData.append('supplier_name', uploadData.supplier_name);
      formData.append('supplier_siren', uploadData.supplier_siren);
      formData.append('invoice_number', uploadData.invoice_number);
      formData.append('invoice_date', uploadData.invoice_date);
      formData.append('due_date', uploadData.due_date || '');
      formData.append('total_ht', uploadData.total_ht);
      formData.append('total_tva', uploadData.total_tva);
      formData.append('total_ttc', uploadData.total_ttc);
      formData.append('format_type', uploadData.format_type);
      formData.append('notes', uploadData.notes || '');

      await axios.post(`${API}/invoices/received`, formData, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      alert('✅ Facture importée avec succès !');
      setShowUploadForm(false);
      setUploadData({
        file: null,
        supplier_name: '',
        supplier_siren: '',
        invoice_number: '',
        invoice_date: new Date().toISOString().split('T')[0],
        due_date: '',
        total_ht: '',
        total_tva: '',
        total_ttc: '',
        format_type: 'pdf-simple',
        notes: ''
      });
      loadReceivedInvoices();
    } catch (error) {
      console.error('Erreur upload facture:', error);
      alert('❌ Erreur lors de l\'import de la facture');
    } finally {
      setLoading(false);
    }
  };

  const updateInvoiceStatus = async (invoiceId, newStatus) => {
    try {
      await axios.patch(
        `${API}/invoices/received/${invoiceId}/status`,
        { status: newStatus },
        { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }
      );
      loadReceivedInvoices();
    } catch (error) {
      console.error('Erreur mise à jour statut:', error);
      alert('❌ Erreur lors de la mise à jour du statut');
    }
  };

  if (showUploadForm) {
    return (
      <div>
        <button
          onClick={() => setShowUploadForm(false)}
          className="mb-6 flex items-center gap-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
          Retour
        </button>

        <h2 className="text-2xl font-bold text-gray-900 mb-6">📤 Importer une facture reçue</h2>

        <form onSubmit={handleUpload} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Fichier</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Fichier PDF/Factur-X *
                </label>
                <input
                  type="file"
                  accept=".pdf,.xml"
                  onChange={handleFileChange}
                  className="w-full"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Format
                </label>
                <select
                  value={uploadData.format_type}
                  onChange={(e) => setUploadData({ ...uploadData, format_type: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                >
                  <option value="pdf-simple">PDF Simple</option>
                  <option value="factur-x">Factur-X</option>
                  <option value="ubl">UBL</option>
                  <option value="cii">CII</option>
                </select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Informations fournisseur</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Nom fournisseur *
                </label>
                <input
                  type="text"
                  value={uploadData.supplier_name}
                  onChange={(e) => setUploadData({ ...uploadData, supplier_name: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  SIREN fournisseur (9 chiffres)
                </label>
                <input
                  type="text"
                  maxLength="9"
                  value={uploadData.supplier_siren}
                  onChange={(e) => setUploadData({ ...uploadData, supplier_siren: e.target.value.replace(/\D/g, '') })}
                  placeholder="123456789"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Détails facture</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    N° Facture *
                  </label>
                  <input
                    type="text"
                    value={uploadData.invoice_number}
                    onChange={(e) => setUploadData({ ...uploadData, invoice_number: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Date facture *
                  </label>
                  <input
                    type="date"
                    value={uploadData.invoice_date}
                    onChange={(e) => setUploadData({ ...uploadData, invoice_date: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Date échéance
                </label>
                <input
                  type="date"
                  value={uploadData.due_date}
                  onChange={(e) => setUploadData({ ...uploadData, due_date: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Total HT *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={uploadData.total_ht}
                    onChange={(e) => setUploadData({ ...uploadData, total_ht: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Total TVA *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={uploadData.total_tva}
                    onChange={(e) => setUploadData({ ...uploadData, total_tva: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Total TTC *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={uploadData.total_ttc}
                    onChange={(e) => setUploadData({ ...uploadData, total_ttc: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  value={uploadData.notes}
                  onChange={(e) => setUploadData({ ...uploadData, notes: e.target.value })}
                  rows="3"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                  placeholder="Notes optionnelles..."
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : '✅ Importer la facture'}
            </Button>
            <Button
              type="button"
              onClick={() => setShowUploadForm(false)}
              variant="outline"
            >
              Annuler
            </Button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">📥 Factures reçues</h2>
          <p className="text-gray-600 mt-1">Import manuel et gestion des factures fournisseurs</p>
        </div>
        <Button
          onClick={() => setShowUploadForm(true)}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700"
        >
          <Upload className="h-4 w-4 mr-2" />
          Importer une facture
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-indigo-600" />
          <p className="text-gray-500 mt-4">Chargement...</p>
        </div>
      ) : receivedInvoices.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-2xl">
          <Download className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 font-medium">Aucune facture reçue</p>
          <p className="text-sm text-gray-400 mt-1">Cliquez sur "Importer une facture" pour commencer</p>
        </div>
      ) : (
        <div className="space-y-3">
          {receivedInvoices.map((invoice) => (
            <div key={invoice.id} className="p-4 border-2 border-gray-200 rounded-xl hover:border-indigo-300 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <Download className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{invoice.invoice_number}</div>
                    <div className="text-sm text-gray-500">{invoice.supplier_name}</div>
                    {invoice.supplier_siren && (
                      <div className="text-xs text-gray-400">SIREN: {invoice.supplier_siren}</div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="font-bold text-gray-900">{invoice.total_ttc}€</div>
                    <div className="text-xs text-gray-500">
                      {new Date(invoice.invoice_date).toLocaleDateString('fr-FR')}
                    </div>
                  </div>
                  <select
                    value={invoice.status}
                    onChange={(e) => updateInvoiceStatus(invoice.id, e.target.value)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium ${
                      invoice.status === 'validated' ? 'bg-green-100 text-green-700' :
                      invoice.status === 'rejected' ? 'bg-red-100 text-red-700' :
                      invoice.status === 'paid' ? 'bg-blue-100 text-blue-700' :
                      invoice.status === 'processing' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}
                  >
                    <option value="received">📥 Reçue</option>
                    <option value="processing">⏳ En traitement</option>
                    <option value="validated">✅ Validée</option>
                    <option value="rejected">❌ Rejetée</option>
                    <option value="paid">💳 Payée</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// =====================================================
// 2. MODULE E-REPORTING
// =====================================================

const EReportingModule = () => {
  const [declarations, setDeclarations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    declaration_type: 'b2c',
    period_start: new Date().toISOString().split('T')[0],
    period_end: new Date().toISOString().split('T')[0],
    total_ht: '',
    total_tva: '',
    total_ttc: '',
    operations_count: '',
    notes: ''
  });

  useEffect(() => {
    loadDeclarations();
  }, []);

  const loadDeclarations = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/e-reporting`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setDeclarations(response.data || []);
    } catch (error) {
      console.error('Erreur chargement déclarations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/e-reporting`, formData, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      alert('✅ Déclaration créée avec succès !');
      setShowCreateForm(false);
      setFormData({
        declaration_type: 'b2c',
        period_start: new Date().toISOString().split('T')[0],
        period_end: new Date().toISOString().split('T')[0],
        total_ht: '',
        total_tva: '',
        total_ttc: '',
        operations_count: '',
        notes: ''
      });
      loadDeclarations();
    } catch (error) {
      console.error('Erreur création déclaration:', error);
      alert('❌ Erreur lors de la création de la déclaration');
    } finally {
      setLoading(false);
    }
  };

  const transmitDeclaration = async (declarationId) => {
    if (!confirm('Confirmer la transmission de cette déclaration au PDP ?')) {
      return;
    }

    try {
      await axios.patch(
        `${API}/e-reporting/${declarationId}/transmit`,
        {},
        { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }
      );
      alert('✅ Déclaration transmise avec succès !');
      loadDeclarations();
    } catch (error) {
      console.error('Erreur transmission:', error);
      alert('❌ Erreur lors de la transmission');
    }
  };

  if (showCreateForm) {
    return (
      <div>
        <button
          onClick={() => setShowCreateForm(false)}
          className="mb-6 flex items-center gap-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
          Retour
        </button>

        <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Nouvelle déclaration E-Reporting</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Type de déclaration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Type d'opération *
                </label>
                <select
                  value={formData.declaration_type}
                  onChange={(e) => setFormData({ ...formData, declaration_type: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                  required
                >
                  <option value="b2c">B2C (Ventes aux particuliers)</option>
                  <option value="export">Export hors UE</option>
                  <option value="intra-ue">Livraison intracommunautaire</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Période début *
                  </label>
                  <input
                    type="date"
                    value={formData.period_start}
                    onChange={(e) => setFormData({ ...formData, period_start: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Période fin *
                  </label>
                  <input
                    type="date"
                    value={formData.period_end}
                    onChange={(e) => setFormData({ ...formData, period_end: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Montants</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Total HT *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.total_ht}
                    onChange={(e) => setFormData({ ...formData, total_ht: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Total TVA *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.total_tva}
                    onChange={(e) => setFormData({ ...formData, total_tva: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Total TTC *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.total_ttc}
                    onChange={(e) => setFormData({ ...formData, total_ttc: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Nombre d'opérations *
                </label>
                <input
                  type="number"
                  value={formData.operations_count}
                  onChange={(e) => setFormData({ ...formData, operations_count: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows="3"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
                  placeholder="Notes optionnelles..."
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : '✅ Créer la déclaration'}
            </Button>
            <Button
              type="button"
              onClick={() => setShowCreateForm(false)}
              variant="outline"
            >
              Annuler
            </Button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">📊 E-Reporting</h2>
          <p className="text-gray-600 mt-1">Déclarations B2C, Export hors UE, Livraisons intra-UE</p>
        </div>
        <Button
          onClick={() => setShowCreateForm(true)}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nouvelle déclaration
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-indigo-600" />
          <p className="text-gray-500 mt-4">Chargement...</p>
        </div>
      ) : declarations.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-2xl">
          <BarChart3 className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 font-medium">Aucune déclaration</p>
          <p className="text-sm text-gray-400 mt-1">Créez votre première déclaration e-reporting</p>
        </div>
      ) : (
        <div className="space-y-3">
          {declarations.map((decl) => (
            <div key={decl.id} className="p-4 border-2 border-gray-200 rounded-xl hover:border-indigo-300 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-yellow-100 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">
                      {decl.declaration_type === 'b2c' && '🛒 B2C - Ventes particuliers'}
                      {decl.declaration_type === 'export' && '🌍 Export hors UE'}
                      {decl.declaration_type === 'intra-ue' && '🇪🇺 Livraison intra-UE'}
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(decl.period_start).toLocaleDateString('fr-FR')} → {new Date(decl.period_end).toLocaleDateString('fr-FR')}
                    </div>
                    <div className="text-xs text-gray-400">
                      {decl.operations_count} opération(s)
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="font-bold text-gray-900">{decl.total_ttc}€</div>
                    <div className="text-xs text-gray-500">TTC</div>
                  </div>
                  {decl.status === 'draft' ? (
                    <Button
                      onClick={() => transmitDeclaration(decl.id)}
                      size="sm"
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      📤 Transmettre
                    </Button>
                  ) : (
                    <Badge className={`
                      ${decl.status === 'transmitted' ? 'bg-blue-100 text-blue-700' : ''}
                      ${decl.status === 'accepted' ? 'bg-green-100 text-green-700' : ''}
                      ${decl.status === 'rejected' ? 'bg-red-100 text-red-700' : ''}
                    `}>
                      {decl.status === 'transmitted' && '📤 Transmise'}
                      {decl.status === 'accepted' && '✅ Acceptée'}
                      {decl.status === 'rejected' && '❌ Rejetée'}
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// =====================================================
// 3. MODULE ARCHIVAGE LÉGAL
// =====================================================

const ArchivesModule = () => {
  const [archives, setArchives] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    loadArchives();
  }, [filterType]);

  const loadArchives = async () => {
    setLoading(true);
    try {
      const params = filterType !== 'all' ? { document_type: filterType } : {};
      const response = await axios.get(`${API}/archives`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        params
      });
      setArchives(response.data || []);
    } catch (error) {
      console.error('Erreur chargement archives:', error);
    } finally {
      setLoading(false);
    }
  };

  const verifyIntegrity = async (archiveId) => {
    try {
      const response = await axios.post(
        `${API}/archives/${archiveId}/verify`,
        {},
        { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }
      );

      if (response.data.integrity_status === 'valid') {
        alert('✅ Intégrité vérifiée : Archive valide');
      } else {
        alert('❌ Intégrité compromise : Archive corrompue');
      }
      loadArchives();
    } catch (error) {
      console.error('Erreur vérification intégrité:', error);
      alert('❌ Erreur lors de la vérification');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🗄️ Archivage légal</h2>
          <p className="text-gray-600 mt-1">Conservation 10 ans avec vérification d'intégrité</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setFilterType('all')}
            variant={filterType === 'all' ? 'default' : 'outline'}
            size="sm"
          >
            Tous
          </Button>
          <Button
            onClick={() => setFilterType('invoice-emitted')}
            variant={filterType === 'invoice-emitted' ? 'default' : 'outline'}
            size="sm"
          >
            Émises
          </Button>
          <Button
            onClick={() => setFilterType('invoice-received')}
            variant={filterType === 'invoice-received' ? 'default' : 'outline'}
            size="sm"
          >
            Reçues
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-indigo-600" />
          <p className="text-gray-500 mt-4">Chargement...</p>
        </div>
      ) : archives.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-2xl">
          <Shield className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 font-medium">Aucune archive</p>
          <p className="text-sm text-gray-400 mt-1">Les documents seront archivés automatiquement</p>
        </div>
      ) : (
        <div className="space-y-3">
          {archives.map((archive) => (
            <div key={archive.id} className="p-4 border-2 border-gray-200 rounded-xl hover:border-indigo-300 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <Shield className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{archive.document_number}</div>
                    <div className="text-sm text-gray-500">{archive.party_name}</div>
                    {archive.party_siren && (
                      <div className="text-xs text-gray-400">SIREN: {archive.party_siren}</div>
                    )}
                    <div className="text-xs text-gray-400 mt-1">
                      Archivé le {new Date(archive.archived_date).toLocaleDateString('fr-FR')}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="font-bold text-gray-900">{archive.total_ttc}€</div>
                    <div className="text-xs text-gray-500">
                      {new Date(archive.document_date).toLocaleDateString('fr-FR')}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      Expire: {new Date(archive.expiration_date).toLocaleDateString('fr-FR')}
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <Badge className={`
                      ${archive.integrity_status === 'valid' ? 'bg-green-100 text-green-700' : ''}
                      ${archive.integrity_status === 'corrupted' ? 'bg-red-100 text-red-700' : ''}
                      ${archive.integrity_status === 'not-checked' ? 'bg-gray-100 text-gray-700' : ''}
                    `}>
                      {archive.integrity_status === 'valid' && '✅ Valide'}
                      {archive.integrity_status === 'corrupted' && '❌ Corrompu'}
                      {archive.integrity_status === 'not-checked' && '⏳ Non vérifié'}
                    </Badge>
                    <Button
                      onClick={() => verifyIntegrity(archive.id)}
                      size="sm"
                      variant="outline"
                    >
                      🔍 Vérifier
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
