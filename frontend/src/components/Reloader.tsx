import { Alert, Button } from 'antd';

export function Reloader({ message, reload }: { message: string; reload: () => void }) {
    return <Alert type="error" showIcon message={message} action={<Button onClick={reload}>重试</Button>} />;
}
