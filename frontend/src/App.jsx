import { Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import DatasetExplorer from './pages/DatasetExplorer';
import TournamentArena from './pages/TournamentArena';
import LivePrediction from './pages/LivePrediction';
import ModelBattleArena from './pages/ModelBattleArena';

// Placeholder Pages (To be created)
const PreprocessingImpact = () => <div className="glass-card"><h1>Preprocessing Impact Analysis</h1><p>Coming soon...</p></div>;
const ClassificationTrack = () => <div className="glass-card"><h1>Classification Track</h1><p>Coming soon...</p></div>;
const RegressionTrack = () => <div className="glass-card"><h1>Regression Track</h1><p>Coming soon...</p></div>;
const FeatureInsights = () => <div className="glass-card"><h1>Feature Insights</h1><p>Coming soon...</p></div>;
const ResearchFindings = () => <div className="glass-card"><h1>Research Findings</h1><p>Coming soon...</p></div>;
const ReportGenerator = () => <div className="glass-card"><h1>Report Generator</h1><p>Coming soon...</p></div>;

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<ExecutiveDashboard />} />
        <Route path="dataset" element={<DatasetExplorer />} />
        <Route path="tournament" element={<TournamentArena />} />
        <Route path="battle" element={<ModelBattleArena />} />
        <Route path="impact" element={<PreprocessingImpact />} />
        <Route path="classification" element={<ClassificationTrack />} />
        <Route path="regression" element={<RegressionTrack />} />
        <Route path="features" element={<FeatureInsights />} />
        <Route path="prediction" element={<LivePrediction />} />
        <Route path="research" element={<ResearchFindings />} />
        <Route path="report" element={<ReportGenerator />} />
      </Route>
    </Routes>
  );
}

export default App;
