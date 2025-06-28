import { useEffect } from 'react';
import TopInputBar from './components/TopInputBar';

function App() {
const handleSubmit = async (goal) => {
  try {
    const res = await fetch('http://localhost:8000/generate-roadmap', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ goal, user_id: 'user123' }),
    });

    const data = await res.json();
    console.log('Roadmap received:', data);
  } catch (err) {
    console.error('API call failed:', err);
  }
};

  // ✅ This runs ONCE when the component mounts
  useEffect(() => {
  const sendGoalToBackend = async () => {
    try {
      const res = await fetch('http://localhost:8000/generate-roadmap', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          goal: 'calculus',    // or dynamically pass a value
          user_id: 'user123',
        }),
      });

      const data = await res.json();
      console.log('Generated roadmap:', data);
    } catch (err) {
      console.error('API error:', err);
    }
  };

  sendGoalToBackend();
}, []);

  return (
    <div className="bg-black h-screen w-screen flex flex-col items-center">
      <TopInputBar onSubmit={handleSubmit} />
    </div>
  );
}

export default App;