const form = document.querySelector('#study-form');
const task = document.querySelector('#task');
const input = document.querySelector('#input');
const output = document.querySelector('#output');
const result = document.querySelector('#result');
const provider = document.querySelector('#provider');
const button = document.querySelector('#submit');
const config = {
  explain: ['Enter a concept or topic', 'Try: Explain how photosynthesis works...', 'A simple explanation with an example.', 'Concept explained'],
  qa: ['What is your question?', 'Try: Which is the largest ocean?', 'Get a concise answer to your question.', 'Answer'],
  quiz: ['Enter a topic or paste a passage', 'Try: The Pacific Ocean is the largest ocean. It covers more than 30% of Earth.', 'Three questions, four choices each.', 'Knowledge check'],
  summarize: ['Paste the text to summarize', 'Paste an educational passage here...', 'Pull out the key ideas.', 'Summary'],
  'learn/recommendations': ['What would you like to learn?', 'Try: SQL for data analysis', 'A practical four-week learning roadmap.', 'Learning path']
};
task.addEventListener('change', () => {
  const [label, placeholder, hint] = config[task.value];
  document.querySelector('#input-label').textContent = label;
  input.placeholder = placeholder;
  document.querySelector('#hint').textContent = hint;
  document.querySelector('#level-row').hidden = task.value !== 'learn/recommendations';
  output.hidden = true;
});
form.addEventListener('submit', async event => {
  event.preventDefault();
  button.disabled = true;
  button.textContent = 'Working…';
  output.hidden = false;
  result.replaceChildren();
  document.querySelector('#result-title').textContent = config[task.value][3];
  provider.textContent = 'Processing';
  try {
    const path = task.value;
    const body = path === 'learn/recommendations' ? {topic: input.value.trim(), level: document.querySelector('#level').value} : {text: input.value.trim()};
    const response = await fetch('/' + path, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Please check your input and try again.');
    provider.textContent = data.provider === 'demo' ? 'No-key demo' : data.provider === 'openrouter' ? 'OpenRouter AI' : 'Gemini AI';
    if (data.questions) renderQuiz(data.questions);
    else { const p = document.createElement('p'); p.className = 'answer'; p.textContent = data.result; result.append(p); }
  } catch (error) { provider.textContent = 'Error'; const p = document.createElement('p'); p.className='error'; p.textContent=error.message; result.append(p); }
  finally { button.disabled = false; button.innerHTML = 'Generate answer <span aria-hidden="true">↗</span>'; output.scrollIntoView({behavior:'smooth', block:'nearest'}); }
});
function renderQuiz(questions) {
  questions.forEach((q, i) => {
    const card = document.createElement('div'); card.className='question';
    const heading = document.createElement('h3'); heading.textContent = `${i+1}. ${q.question}`; card.append(heading);
    const feedback = document.createElement('p'); feedback.className='feedback';
    q.options.forEach(option => {
      const choice = document.createElement('button'); choice.type='button'; choice.className='choice'; choice.textContent=option;
      choice.addEventListener('click', () => {
        card.querySelectorAll('.choice').forEach(b => { b.disabled=true; if (b.textContent===q.answer) b.classList.add('correct'); });
        if (option!==q.answer) choice.classList.add('incorrect');
        feedback.textContent = option===q.answer ? 'Correct!' : `Correct answer: ${q.answer}`;
      }); card.append(choice);
    }); card.append(feedback); result.append(card);
  });
}
