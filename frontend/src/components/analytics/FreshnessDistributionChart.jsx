import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Mapping grades to the CSS variables used in the theme
const COLORS = {
  'Fresh': '#10b981',     // success-green
  'Good': '#3b82f6',      // some blue for distinction if desired, or orange
  'Old': '#f59e0b',       // warning yellow
  'Spoiled': '#ef4444',   // red
  'Default': '#64748b'    // slate
};

export default function FreshnessDistributionChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="flex h-full items-center justify-center text-muted">No data available</div>;
  }

  return (
    <div style={{ width: '100%', height: '300px' }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#8884d8"
            animationDuration={800}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name] || COLORS['Default']} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px' }}
            itemStyle={{ color: '#fff' }}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
