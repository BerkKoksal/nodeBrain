import { useEffect } from 'react';
import TopInputBar from './components/TopInputBar';

function App() {
  const handleSubmit = (topic) => {
    console.log('User wants to learn about:', topic);
    // Later, you’ll send this to the backend
  };

  // ✅ This runs ONCE when the component mounts
  useEffect(() => {
    fetch('http://localhost:8000')
      .then((res) => res.json())
      .then((data) => console.log('Backend says:', data))
      .catch((err) => console.error('API Error:', err));
  }, []);

  return (
    <div className="bg-black h-screen w-screen flex flex-col items-center">
      <TopInputBar onSubmit={handleSubmit} />
    </div>
  );
}

export default App;