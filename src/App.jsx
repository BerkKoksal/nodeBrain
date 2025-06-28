import TopInputBar from './components/TopInputBar';
import NodeMap from './components/NodeMap';



function App() {

  const handleSubmit = (topic) => {
    console.log('User wants to learn about ', topic);
  }


  return (
    <div className="bg-black h-screen w-screen flex flex-col">
      <TopInputBar onSubmit={handleSubmit}/>
      <NodeMap />
      
    </div>

  )
}

export default App
