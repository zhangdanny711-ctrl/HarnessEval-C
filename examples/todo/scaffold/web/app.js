const title = document.querySelector('[data-testid=task-title]');
const priority = document.querySelector('[data-testid=priority]');
const filter = document.querySelector('[data-testid=priority-filter]');
const list = document.querySelector('[data-testid=task-list]');

async function render() {
  const query = filter.value ? `?priority=${filter.value}` : '';
  const response = await fetch(`/api/tasks${query}`);
  const body = await response.json();
  list.replaceChildren(...body.data.map(task => {
    const item = document.createElement('li');
    item.textContent = `${task.title} (${task.priority})`;
    item.dataset.testid = task.completed ? 'task-complete' : 'task-open';
    return item;
  }));
}

document.querySelector('[data-testid=add-task]').addEventListener('click', async () => {
  await fetch('/api/tasks', {method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title: title.value, priority: priority.value})});
  await render();
});
filter.addEventListener('change', () => { history.replaceState({}, '', filter.value ? `/?priority=${filter.value}` : '/'); render(); });
render();

