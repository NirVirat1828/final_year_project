import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const COLORS = {
  'Fresh': '#10b981',
  'Good': '#3b82f6',
  'Old': '#f59e0b',
  'Spoiled': '#ef4444',
  'Default': '#64748b'
};

export default function AverageConfidenceChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="flex h-full items-center justify-center text-muted">No data available</div>;
  }

  // Format tooltip to show percentage
  const formatTooltip = (value) => {
    return [`${(value * 100).toFixed(1)}%`, 'Avg Confidence'];
  };

  const formatYAxis = (tickItem) => {
    return `${(tickItem * 100).toFixed(0)}%`;
  };

  return (
    <div style={{ width: '100%', height: '300px' }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
          <XAxis 
            dataKey="name" 
            stroke="rgba(255,255,255,0.5)" 
            tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} 
          />
          <YAxis 
            stroke="rgba(255,255,255,0.5)" 
            tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} 
            tickFormatter={formatYAxis}
            domain={[0, 1]}
          />
          <Tooltip 
            formatter={formatTooltip}
            contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px' }}
            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
          <Bar 
            dataKey="avgConfidence" 
            name="Average Confidence" 
            radius={[4, 4, 0, 0]}
            animationDuration={1000}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name] || COLORS['Default']} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
