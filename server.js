import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

app.get('*', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>HRM MVP Repository</title>
        <style>
          body { font-family: system-ui, -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #f8fafc; color: #0f172a; }
          .container { text-align: center; max-width: 650px; padding: 2.5rem; background: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
          h1 { color: #0f172a; margin-top: 0; }
          p { color: #475569; line-height: 1.6; }
          .terminal { text-align: left; background: #0f172a; color: #f8fafc; padding: 1.5rem; border-radius: 8px; margin-top: 1.5rem; font-family: monospace; font-size: 0.9rem; overflow-x: auto; }
          .terminal .comment { color: #64748b; }
          .terminal .command { color: #38bdf8; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>🚀 Cấu trúc HRM MVP đã sẵn sàng</h1>
          <p>Dự án đã được cấu trúc thành 2 thư mục riêng biệt: <strong>Backend (Cấu trúc Clean Architecture với FastAPI)</strong> và <strong>Frontend (Angular)</strong> đúng theo yêu cầu của bạn, tất cả các file rác đã được dọn dẹp.</p>
          <p><em>Lưu ý: Môi trường Sandbox Preview này chỉ chạy được Node.js (JavaScript/TypeScript). Để chạy ứng dụng Python FastAPI và Angular, vui lòng Export/Download code về máy và chạy local:</em></p>
          
          <div class="terminal">
            <span class="comment"># 1. Chạy Backend (Terminal 1)</span><br/>
            <span class="command">cd backend</span><br/>
            <span class="command">pip install -r requirements.txt</span><br/>
            <span class="command">uvicorn main:app --reload</span><br/>
            <br/>
            <span class="comment"># 2. Chạy Test cho UseCase (Terminal 2)</span><br/>
            <span class="command">cd backend</span><br/>
            <span class="command">pytest tests/test_approve_leave_usecase.py -v</span><br/>
          </div>
        </div>
      </body>
    </html>
  `);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(\`Placeholder server running on port \${PORT}\`);
});
