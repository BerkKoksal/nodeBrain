export default function TopInputBar({onSubmit}){
    return(
        <div className="w-full flex flex-col items-center mt-4">
            <h2 className="text-white text-xl mb-2 font-minecraft">I want to learn</h2>
            <input className="border-2 border-white bg-transparent text-white px-4 py-2 w-md  text-center rounded font-minecraft" 
            type="text"
            placeholder="Enter a topic..."
            onKeyDown={(e) => {
                if (e.key === 'Enter') onSubmit?.(e.target.value);
            }}
            />
        </div>
    );
}