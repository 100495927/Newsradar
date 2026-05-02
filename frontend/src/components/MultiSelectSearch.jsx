import { useState, useRef, useEffect } from 'react'

function MultiSelectSearch({ options = [], selected = [], onChange, placeholder = 'Buscar...' }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const containerRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false)
        setQuery('')
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const filtered = options.filter((o) =>
    o.label.toLowerCase().includes(query.toLowerCase())
  )

  const toggle = (id) => {
    if (selected.includes(id)) {
      onChange(selected.filter((s) => s !== id))
    } else {
      onChange([...selected, id])
    }
  }

  const remove = (id, e) => {
    e.stopPropagation()
    onChange(selected.filter((s) => s !== id))
  }

  const selectedOptions = options.filter((o) => selected.includes(o.id))

  return (
    <div ref={containerRef} className="relative">
      {/* Selected chips */}
      {selectedOptions.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-2">
          {selectedOptions.map((o) => (
            <span
              key={o.id}
              className="inline-flex items-center gap-1 bg-primary-container/10 text-primary-container text-xs font-medium px-2 py-1 rounded-full"
            >
              <span className="max-w-[160px] truncate">{o.label}</span>
              <button
                type="button"
                onClick={(e) => remove(o.id, e)}
                className="material-symbols-outlined text-[14px] leading-none hover:text-red-500"
              >
                close
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Search input */}
      <div
        className="flex items-center gap-2 w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 cursor-text"
        onClick={() => setOpen(true)}
      >
        <span className="material-symbols-outlined text-slate-400 text-[18px]">search</span>
        <input
          className="flex-1 bg-transparent outline-none text-sm text-slate-800 placeholder-slate-400"
          placeholder={selected.length > 0 ? `${selected.length} seleccionado${selected.length > 1 ? 's' : ''}` : placeholder}
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true) }}
          onFocus={() => setOpen(true)}
        />
        <span className="material-symbols-outlined text-slate-400 text-[18px]">
          {open ? 'expand_less' : 'expand_more'}
        </span>
      </div>

      {/* Dropdown */}
      {open && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-52 overflow-y-auto">
          {filtered.length === 0 ? (
            <p className="px-4 py-3 text-sm text-slate-400">Sin resultados</p>
          ) : (
            filtered.map((o) => {
              const isSelected = selected.includes(o.id)
              return (
                <button
                  key={o.id}
                  type="button"
                  onClick={() => toggle(o.id)}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm hover:bg-slate-50 transition-colors ${
                    isSelected ? 'bg-primary-container/5' : ''
                  }`}
                >
                  <span
                    className={`material-symbols-outlined text-[18px] flex-shrink-0 ${
                      isSelected ? 'text-primary-container' : 'text-slate-300'
                    }`}
                  >
                    {isSelected ? 'check_box' : 'check_box_outline_blank'}
                  </span>
                  <span className="truncate text-slate-700">{o.label}</span>
                </button>
              )
            })
          )}
        </div>
      )}
    </div>
  )
}

export default MultiSelectSearch
