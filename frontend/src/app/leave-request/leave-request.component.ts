import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-leave-request',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="p-6 bg-white border border-slate-200 rounded-xl shadow-sm max-w-sm">
        <h2 class="text-xl font-bold mb-4 text-slate-800">Leave Request #{{ requestId }}</h2>
        <div class="flex gap-4">
            <button 
                (click)="approveLeave()" 
                class="px-4 py-2 bg-emerald-600 text-white rounded text-sm font-bold shadow-sm hover:bg-emerald-700 disabled:opacity-50"
                [disabled]="loading"
            >
                {{ loading ? 'Processing...' : 'Approve' }}
            </button>
        </div>
        
        <p *ngIf="message" class="mt-4 text-sm font-medium" 
            [ngClass]="{'text-emerald-600': success, 'text-red-600': !success}">
            {{ message }}
        </p>
    </div>
    `,
})
export class LeaveRequestComponent implements OnInit {
    requestId: number | null = null;
    message = '';
    success = false;
    loading = false;
    
    // Dependency Injection thông qua hàm inject() của Angular
    private http = inject(HttpClient);
    private route = inject(ActivatedRoute);

    ngOnInit() {
        this.route.paramMap.subscribe(params => {
            const id = params.get('id');
            if (id) {
                this.requestId = parseInt(id, 10);
            }
        });
    }

    approveLeave() {
        if (!this.requestId) return;
        this.loading = true;
        
        // Mock token (Thử giả phân quyền Admin)
        const headers = { 'x-user-role': 'Admin' };
        
        // Gọi API sử dụng Nest Calls tương ứng Backend
        this.http.post<{success: boolean, message: string}>(`/api/leaves/${this.requestId}/approve`, {}, { headers })
        .subscribe({
            next: (res) => {
                this.success = res.success;
                this.message = res.message;
                this.loading = false;
            },
            error: (err) => {
                this.success = false;
                this.message = err.error?.detail || 'Lỗi server xảy ra!';
                this.loading = false;
            }
        });
    }
}
