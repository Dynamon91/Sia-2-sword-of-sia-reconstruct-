static void lever_step(Game *g,unsigned input){
  unsigned pressed=input&~(unsigned)g->previous;
  /* The World 1 lever sits on the right-hand side of the entry view; activating it
     toggles the persistent gate state while the player is grounded and near the switch. */
  if(g->area==12 && !g->progress.lever_activated && g->grounded &&
     g->x/FP>=120 && g->x/FP<=170 && g->y/FP>=18 && g->y/FP<=40 &&
     (pressed&(JUMP|ATTACK|UP|DOWN))){
    level_set_lever_state(&g->progress,1);
  }
}
static void barrier_step(Game *g){
  if(g->area!=12 || g->progress.barrier_open)return;
  /* Keep the player right of the gate until the lever has opened it. The gate is
     anchored on the entry-side wall, so the left edge must not cross the threshold. */
  if(g->vx<0 && g->x/FP+PLAYER_W>130 && g->x/FP<150){
    g->x=130*FP;g->vx=0;
  }
}
