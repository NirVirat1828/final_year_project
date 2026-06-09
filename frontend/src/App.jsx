import { Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import DatasetExplorer from './pages/DatasetExplorer';
import TournamentArena from './pages/TournamentArena';
import LivePrediction from './pages/LivePrediction';
import ModelBattleArena from './pages/ModelBattleArena';
import PreprocessingImpact from './pages/PreprocessingImpact';
import ClassificationTrack from './pages/ClassificationTrack';
import RegressionTrack from './pages/RegressionTrack';
import FeatureInsights from './pages/FeatureInsights';
import ResearchFindings from './pages/ResearchFindings';
import ReportGenerator from './pages/ReportGenerator';

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
