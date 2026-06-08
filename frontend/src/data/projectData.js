export const projectFacts = [
  'Non-destructive orange freshness analysis',
  'Two outputs: grade classification and regression',
  'Uses sensor batches, engineered features, and stacking models',
]

export const workflowStages = [
  {
    title: '1. Data',
    text: 'Sensor CSVs, target labels, and blind-test batches are organized under datasets/.',
  },
  {
    title: '2. Features',
    text: 'Raw readings are smoothed and turned into DCT, statistical, and enhanced features.',
  },
  {
    title: '3. Models',
    text: 'Track A classifies freshness, while Track B predicts storage days and folic acid.',
  },
]

export const trackCards = [
  {
    title: 'Track A',
    subtitle: 'Freshness grade classification',
    detail: 'Stacking ensemble for A, B, C, D output.',
  },
  {
    title: 'Track B',
    subtitle: 'Storage day prediction',
    detail: 'Regression model used for time-since-harvest estimation.',
  },
  {
    title: 'Folic acid',
    subtitle: 'Concentration estimation',
    detail: 'Predicts µM concentration from the same sensor workflow.',
  },
]

export const datasetItems = [
  {
    path: 'datasets/X_features.csv',
    note: 'Baseline feature table.',
  },
  {
    path: 'datasets/X_features_enhanced.csv',
    note: 'Enhanced feature table used for the newer experiments.',
  },
  {
    path: 'datasets/y_targets.csv',
    note: 'Batch, day, and concentration labels.',
  },
  {
    path: 'datasets/test_dataset_blind/',
    note: 'Unseen evaluation batches.',
  },
]

export const keyPaths = [
  'src/preprocessing/',
  'src/training/',
  'src/benchmarking/',
  'src/inference/',
  'src/visualization/',
  'docs/reports/',
]

export const runCommands = [
  'cd frontend',
  'npm install',
  'npm run dev',
]
