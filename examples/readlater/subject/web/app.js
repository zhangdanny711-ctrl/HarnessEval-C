const form = document.querySelector('[data-testid=save-form]');
const titleInput = document.querySelector('[data-testid=article-title]');
const message = document.querySelector('[data-testid=message]');
const queue = document.querySelector('[data-testid=reading-queue]');

async function request(path, options = {}) {
  const response = await fetch(path, options);
  return {response, body: await response.json()};
}

async function render() {
  const {body} = await request('/api/articles');
  const items = body.data.map(article => {
    const row = document.createElement('li');
    row.dataset.title = article.title;
    row.dataset.read = String(article.read);

    const label = document.createElement('span');
    label.textContent = article.title;
    row.append(label);

    if (!article.read) {
      const button = document.createElement('button');
      button.dataset.testid = 'mark-read';
      button.textContent = 'Mark read';
      button.addEventListener('click', async () => {
        await request(`/api/articles/${article.id}/read`, {method: 'PATCH'});
        await render();
      });
      row.append(button);
    }
    return row;
  });
  queue.replaceChildren(...items);
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const {response, body} = await request('/api/articles', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title: titleInput.value}),
  });
  message.textContent = response.ok ? '' : body.message;
  if (response.ok) {
    titleInput.value = '';
    await render();
  }
});

render();
