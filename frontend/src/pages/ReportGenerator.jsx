import { useState } from 'react';
import { FileText, Download, FileJson, Presentation, File } from 'lucide-react';

const sections = [
  { id: 'dataset', label: 'Dataset Analysis' },
  { id: 'tournament', label: 'Tournament Results' },
  { id: 'classification', label: 'Classification Results' },
  { id: 'regression', label: 'Regression Results' },
  { id: 'feature', label: 'Feature Importance' },
  { id: 'findings', label: 'Research Findings' }
];

export default function ReportGenerator() {
  const [selected, setSelected] = useState(sections.map(s => s.id));
  const [isGenerating, setIsGenerating] = useState(false);

  const toggleSection = (id) => {
    setSelected(prev => prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]);
  };

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => setIsGenerating(false), 2000);
  };

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-h1 flex items-center gap-4"><FileText className="text-primary-orange" size={32} /> Report Generator</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* Configuration */}
        <section className="glass-card flex flex-col gap-6">
          <h2 className="text-h2">Configuration</h2>
          <p className="text-muted" style={{ fontSize: '0.875rem' }}>Select the modules to include in the final export.</p>
          
          <div className="flex flex-col gap-3">
            {sections.map(section => (
              <label key={section.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
                <input 
                  type="checkbox" 
                  checked={selected.includes(section.id)}
                  onChange={() => toggleSection(section.id)}
                  style={{ width: '18px', height: '18px', accentColor: 'var(--primary-orange)' }}
                />
                <span style={{ fontWeight: 500 }}>{section.label}</span>
              </label>
            ))}
          </div>

          <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <p className="text-muted mb-4" style={{ fontSize: '0.875rem' }}>Estimated length: {selected.length * 2 + 1} pages</p>
            <button 
              className="btn btn-primary w-full" 
              onClick={handleGenerate}
              disabled={isGenerating || selected.length === 0}
            >
              {isGenerating ? 'Compiling Document...' : 'Generate Preview'}
            </button>
          </div>
        </section>

        {/* Preview and Export */}
        <section className="flex flex-col gap-6">
          <div className="glass-card bg-gradient-dark" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 className="text-h2 text-white mb-1">Export Options</h2>
              <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.875rem' }}>Download the final report in your preferred format.</p>
            </div>
            <div className="flex gap-2">
              <button className="btn btn-outline" style={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}><File size={16} /> PDF</button>
              <button className="btn btn-outline" style={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}><FileJson size={16} /> DOCX</button>
              <button className="btn btn-outline" style={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}><Presentation size={16} /> PPT</button>
            </div>
          </div>

          <div className="glass-card" style={{ flex: 1, minHeight: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', backgroundColor: '#E2E8F0', border: '1px solid var(--border-color)', backgroundImage: 'linear-gradient(45deg, #cbd5e1 25%, transparent 25%, transparent 75%, #cbd5e1 75%, #cbd5e1), linear-gradient(45deg, #cbd5e1 25%, transparent 25%, transparent 75%, #cbd5e1 75%, #cbd5e1)', backgroundSize: '20px 20px', backgroundPosition: '0 0, 10px 10px' }}>
            {/* Mock A4 Paper Preview */}
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              key={isGenerating ? 'loading' : 'done'}
              style={{ width: '300px', height: '420px', backgroundColor: 'white', boxShadow: 'var(--shadow-lg)', padding: '2rem', display: 'flex', flexDirection: 'column' }}
            >
              {isGenerating ? (
                <div className="flex flex-col items-center justify-center h-full gap-4 text-muted">
                  <div className="animate-pulse"><Download size={32} /></div>
                  <p>Rendering...</p>
                </div>
              ) : (
                <>
                  <div style={{ borderBottom: '2px solid var(--primary-orange)', paddingBottom: '1rem', marginBottom: '1rem' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>Orange Freshness</h3>
                    <p className="text-muted" style={{ fontSize: '0.75rem' }}>Final Research Report</p>
                  </div>
                  <div className="flex flex-col gap-2">
                    {selected.map(id => (
                      <div key={id} style={{ height: '8px', width: Math.random() * 50 + 50 + '%', backgroundColor: 'var(--border-color)', borderRadius: '4px' }} />
                    ))}
                  </div>
                </>
              )}
            </motion.div>
          </div>
        </section>
      </div>
    </div>
  );
}
