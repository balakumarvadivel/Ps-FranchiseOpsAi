import { LineChart, Line, ResponsiveContainer } from "recharts";

export function Sparkline({ data = [], color = "#3b82f6" }) {
  if (!data.length) return null;
  return (
    <ResponsiveContainer width="100%" height={36}>
      <LineChart data={data.map((v, i) => ({ i, v }))}>
        <Line type="monotone" dataKey="v" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
