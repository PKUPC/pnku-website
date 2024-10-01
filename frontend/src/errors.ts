export class NeverError extends Error {
    constructor(message?: string) {
        super(message ? message : '');
        this.name = 'NeverError';
    }
}

export class InfoError extends Error {
    constructor(message?: string) {
        super(message ? message : '');
        this.name = 'InfoError';
    }
}

export class NotStaffError extends Error {
    constructor(message?: string) {
        super(message ? message : '');
        this.name = 'NotStaffError';
    }
}

export class DataError extends Error {
    public title: string | undefined;

    constructor(message?: string, title?: string) {
        super(message ? message : '');
        this.name = 'DataError';
        this.title = title;
    }
}
