import { WebsocketProvider } from 'y-websocket';
import * as Y from 'yjs';

import { SYNC_ROOT } from '@/constants';

export class YClient {
    public doc: Y.Doc;
    public provider: WebsocketProvider;
    public roomId: string;
    public stopped: boolean = false;

    constructor(roomId: string) {
        this.roomId = roomId;
        this.doc = new Y.Doc();

        const url = new URL(SYNC_ROOT, window.location.href);
        url.protocol = url.protocol === 'http:' ? 'ws:' : 'wss:';

        this.provider = new WebsocketProvider(url.href, roomId, this.doc, {
            connect: false,
            params: {
                rem: window.rem ?? 'undefined',
                ram: window.ram ?? 'undefined',
            },
        });

        this.setupListeners();
    }

    connect() {
        this.provider.connect();
    }

    private statusHandler = (event: { status: string }) => {
        console.log(`[YClient ${this.roomId}] status:`, event.status);
    };

    private syncHandler = (isSynced: boolean) => {
        console.log(`[YClient ${this.roomId}] synced:`, isSynced);
    };

    private connectionCloseHandler = (event: CloseEvent | null) => {
        if (event) {
            console.log(`[YClient ${this.roomId}] connection closed:`, {
                code: event.code,
                reason: event.reason,
                wasClean: event.wasClean,
            });

            if (event.code === 1000) {
                console.log(`[YClient ${this.roomId}] connection closed normally`);
                return;
            } else if (event.code === 4337) {
                console.log(`[YClient ${this.roomId}] server closed connection, reason: ${event.reason}`);
                this.stopped = true;
                this.destroy();
                return;
            } else {
                console.log(`[YClient ${this.roomId}] connection closed, reason: ${event.reason}`);
                this.stopped = true;
                this.destroy();
                return;
            }
        } else {
            console.log(
                `[YClient ${this.roomId}] connection closed (no event details, maybe no message received in a long time)`,
            );
        }
    };

    private connectionErrorHandler = (event: Event) => {
        console.error(`[YClient ${this.roomId}] connection error:`, event);

        if (event instanceof ErrorEvent) {
            console.error(`[YClient ${this.roomId}] error message:`, event.message);
        }
    };

    private handleAwarenessChange = ({
        added,
        updated,
        removed,
    }: {
        added: number[];
        updated: number[];
        removed: number[];
    }) => {
        const states = this.provider.awareness.getStates();
        const usersMap = new Map<number, any>();

        states.forEach((state, clientId) => {
            if (state.user) {
                usersMap.set(clientId, state);
            }
        });

        // 打印变化日志
        console.log('local client id:', this.provider.awareness.clientID);
        console.log('Added users:', added);
        console.log('Updated users:', updated);
        console.log('Removed users:', removed);
        console.log(usersMap);
    };

    private setupListeners() {
        this.provider.on('status', this.statusHandler);
        this.provider.on('sync', this.syncHandler);
        this.provider.on('connection-close', this.connectionCloseHandler);
        this.provider.on('connection-error', this.connectionErrorHandler);
        this.provider.awareness.on('change', this.handleAwarenessChange);
    }

    destroy() {
        this.provider.off('status', this.statusHandler);
        this.provider.off('sync', this.syncHandler);
        this.provider.off('connection-close', this.connectionCloseHandler);
        this.provider.off('connection-error', this.connectionErrorHandler);
        this.provider.awareness.off('change', this.handleAwarenessChange);
        this.provider.disconnect();
        this.provider.destroy();
        this.doc.destroy();
        console.log(`[YClient ${this.roomId}] destroyed`);
    }
}
